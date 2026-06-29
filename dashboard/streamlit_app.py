import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.modules.enrichment import enrich_company
from app.modules.icp_scoring import score_lead
from app.modules.email_gen import generate_email
from app.modules.chat_assistant import ask_pipeline
from app.modules.gmail_sender import send_email

@st.cache_data
def load_data():
    try:
        import requests
        api_key = st.secrets.get("HUBSPOT_API_KEY", None)
        if api_key:
            headers = {"Authorization": f"Bearer {api_key}"}
            url = "https://api.hubapi.com/crm/v3/objects/contacts"
            params = {"limit": 100, "properties": "firstname,email,hs_lead_status,createdate,num_employees,annualrevenue,hs_analytics_source"}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                contacts = []
                for result in data["results"]:
                    props = result.get("properties", {})
                    contacts.append({"employees": props.get("num_employees") or "10-50", "revenue": props.get("annualrevenue") or "1-10M", "source": props.get("hs_analytics_source") or "website", "icp_score": min(100, max(40, len(props.get("email","x") or "x") * 3 + 40)), "status": (props.get("hs_lead_status") or "warm").lower(), "date_added": (props.get("createdate") or "2024-01-01")[:10]})
                return pd.DataFrame(contacts)
    except Exception as e:
        st.warning(f"HubSpot failed: {e}")
    import os
    path = "leads_dataset.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

st.set_page_config(page_title="RevenueOS", layout="wide")
st.title("RevenueOS")
st.caption("AI-powered lead enrichment, scoring, and outreach automation")


df = load_data()
if df.empty:
    st.warning("No data found. Check leads_dataset.csv")
    st.stop()

# Add missing columns with defaults if not present
for col, default in [('industry', 'Unknown'), ('jobtitle', 'Unknown'), ('source', 'Unknown'), ('status', 'warm'), ('icp_score', 50), ('days_inactive', 0), ('decay_status', 'Watch'), ('num_employees', 'Unknown'), ('annualrevenue', 'Unknown')]:
    if col not in df.columns:
        df[col] = default
df["date_added"] = pd.to_datetime(df["date_added"])
df["days_inactive"] = (pd.Timestamp.today() - df["date_added"]).dt.days

with st.sidebar:
    st.header("Add New Lead")
    first_name = st.text_input("First Name", "Sarah")
    last_name = st.text_input("Last Name", "Johnson")
    email = st.text_input("Email", "sarah@example.com")
    company = st.text_input("Company", "TechCorp")
    job_title = st.text_input("Job Title", "CEO")
    source = st.selectbox("Source", ["referral", "linkedin", "website", "cold_email", "webinar", "conference", "inbound"])
    analyze = st.button("Analyze Lead", use_container_width=True)

if analyze:
    with st.spinner("Running AI analysis..."):
        lead_data = {"first_name": first_name, "last_name": last_name, "email": email, "company": company, "job_title": job_title, "source": source}
        company_data = enrich_company(company)
        scoring = score_lead(lead_data, company_data)
        grade = scoring["grade"]
        score = scoring["score"]
        email_content = generate_email(lead_data, company_data, scoring) if grade == "HOT" else None
        st.session_state["analysis"] = {"lead_data": lead_data, "company_data": company_data, "scoring": scoring, "grade": grade, "score": score, "email_content": email_content}

tab1, tab2, tab3, tab4, tab_decay, tab_brief, tab_intel = st.tabs(["Pipeline Dashboard", "AI Assistant", "All Leads", "Analytics", "Decay Alerts", "GTM Brief", "Account Intel"])


with tab1:
    if "analysis" in st.session_state:
        r = st.session_state["analysis"]
        st.subheader(f"Lead Analysis: {r['lead_data']['first_name']} {r['lead_data']['last_name']}")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("ICP Score", f"{r['score']}/100")
        col2.metric("Grade", r['grade'])
        col3.metric("Industry", r["company_data"].get("industry", "Unknown"))
        col4.metric("Employees", r["company_data"].get("employees", 0))
        col5.metric("Revenue", r["company_data"].get("revenue", "Unknown"))
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Lead Info")
            st.write(f"**Name:** {r['lead_data']['first_name']} {r['lead_data']['last_name']}")
            st.write(f"**Title:** {r['lead_data']['job_title']}")
            st.write(f"**Company:** {r['lead_data']['company']}")
            st.write(f"**Industry:** {r['company_data'].get('industry', 'Unknown')}")
            st.write(f"**Revenue:** {r['company_data'].get('revenue', 'Unknown')}")
        with c2:
            st.subheader("AI Generated Email")
            if r["grade"] == "HOT" and r["email_content"]:
                st.text_area("Generated Email", value=r["email_content"], height=200)
                st.success("Email generated by Claude AI")
                col_a, col_b = st.columns(2)
                col_a.download_button("Download", r["email_content"], file_name="email.txt")
                if col_b.button("Send via Gmail"):
                    success, msg = send_email(r["lead_data"]["email"], f"Quick note for {r['lead_data']['first_name']}", r["email_content"])
                    if success:
                        st.success(f"Email sent to {r['lead_data']['email']}")
                    else:
                        st.error(f"Failed: {msg}")
            else:
                st.info(f"Score is {r['score']}/100  AI email triggers at 40+")
        st.divider()

    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Leads", len(df))
        col2.metric("Hot", len(df[df["status"]=="hot"]))
        col3.metric("Warm", len(df[df["status"]=="warm"]))
        col4.metric("Cold", len(df[df["status"]=="cold"]))
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.histogram(df, x="icp_score", color="status", title="ICP Score Distribution", color_discrete_map={"hot":"#ff4b4b","warm":"#ffa500","cold":"#4b9dff"})
            fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            if "industry" in df.columns:
                fig2 = px.bar(df["industry"].value_counts().reset_index(), x="industry", y="count", title="Leads by Industry", color_discrete_sequence=["#7c83fd"])
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)
        c3, c4 = st.columns(2)
        with c3:
            fig3 = px.pie(df, names="source", title="Lead Sources")
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig3, use_container_width=True)
        with c4:
            trend = df.groupby("date_added").size().reset_index(name="leads")
            fig4 = px.line(trend, x="date_added", y="leads", title="Leads Over Time", color_discrete_sequence=["#7c83fd"])
            fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig4, use_container_width=True)

with tab2:
    st.subheader("Ask Anything About Your Pipeline")
    if df.empty:
        st.warning("No dataset loaded.")
    else:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        st.write("**Try asking:**")
        cols = st.columns(3)
        suggestions = ["Which industry has the most hot leads?", "Who should I contact first?", "What is my average ICP score?", "Which source converts best?", "How many LinkedIn leads?", "Top 5 leads to prioritize"]
        for i, s in enumerate(suggestions):
            if cols[i % 3].button(s, key=f"sug_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": s})
                with st.spinner("Thinking..."):
                    answer = ask_pipeline(s, df)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()
        question = st.chat_input("Ask about your pipeline...")
        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Thinking..."):
                answer = ask_pipeline(question, df)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

with tab3:
    st.subheader("Full Lead Database")
    if df.empty:
        st.warning("No leads found.")
    else:
        col1, col2, col3 = st.columns(3)
        status_filter = col1.selectbox("Filter by Status", ["All", "hot", "warm", "cold"])
        industry_filter = col2.selectbox("Filter by Industry", ["All"] + sorted(df["industry"].unique().tolist() if "industry" in df.columns else []))
        source_filter = col3.selectbox("Filter by Source", ["All"] + sorted(df["source"].unique().tolist()))
        filtered = df.copy()
        if status_filter != "All":
            filtered = filtered[filtered["status"] == status_filter]
        if industry_filter != "All":
            filtered = filtered["industry" in filtered.columns and filtered["industry"] == industry_filter]
        if source_filter != "All":
            filtered = filtered[filtered["source"] == source_filter]
        st.write(f"Showing **{len(filtered)}** leads")
        st.dataframe(filtered.sort_values("icp_score", ascending=False), use_container_width=True)
        csv = filtered.to_csv(index=False)
        st.download_button("Export CSV", csv, file_name="filtered_leads.csv", mime="text/csv")


        st.divider()
        st.subheader("Lead Score Explainer")
        st.caption("Select a lead to understand why it scored the way it did.")

        lead_index = st.selectbox(
            "Select a lead by index",
            df.index,
            format_func=lambda x: f"Lead #{x} — {df.loc[x, 'source']} | {df.loc[x, 'status']} | Score: {df.loc[x, 'icp_score']}"
        )

        if st.button("Explain This Score"):
            selected = df.loc[lead_index]

            prompt = f"""
You are a B2B sales analyst. Explain in plain English why this lead received an ICP score of {selected['icp_score']} out of 100.

Lead details:
- Status: {selected['status']}
- Source: {selected['source']}
- Company size (employees): {selected['employees']}
- Revenue range: {selected['revenue']}
- Days in pipeline: {selected['days_inactive']}
- ICP Score: {selected['icp_score']}
Give a 3-5 sentence explanation. Be specific and direct. Mention what's working in their favor and what's holding the score back. No emojis. No fluff.
"""

            import anthropic
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

            with st.spinner("Analyzing lead..."):
                message = client.messages.create(
                    model="claude-sonnet-4-6",
                  max_tokens=512,
               messages=[{"role": "user", "content": prompt}]
                )

            explanation = message.content[0].text
            st.markdown(f"**Score: {selected['icp_score']}/100**")
            st.markdown(explanation)


with tab4:
    st.subheader("Lead Trend Analytics")
    st.caption("Conversion rates, pipeline value, and source performance")

    if df.empty:
        st.warning("No dataset loaded.")
    else:
        # KPI row
        hot_rate = round(len(df[df["status"]=="hot"]) / len(df) * 100, 1)
        warm_rate = round(len(df[df["status"]=="warm"]) / len(df) * 100, 1)
        avg_score = round(df["icp_score"].mean(), 1)
        top_source = df["source"].value_counts().index[0]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Hot Conversion Rate", f"{hot_rate}%")
        k2.metric("Warm Rate", f"{warm_rate}%")
        k3.metric("Avg ICP Score", avg_score)
        k4.metric("Top Source", top_source.title())

        st.divider()

        c1, c2 = st.columns(2)

        with c1:
            # Conversion rate by source
            source_conv = df.groupby("source").apply(
                lambda x: round(len(x[x["status"]=="hot"]) / len(x) * 100, 1)
            ).reset_index()
            source_conv.columns = ["source", "hot_rate"]
            source_conv = source_conv.sort_values("hot_rate", ascending=False)
            fig1 = px.bar(source_conv, x="source", y="hot_rate",
                title="Hot Lead Rate by Source (%)",
                color="hot_rate",
                color_continuous_scale=["#1A1D2E", "#00C48C"])
            fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color":"white"})
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            # Avg ICP score by industry
            industry_score = df.groupby("industry") if "industry" in df.columns else df.groupby("status")["icp_score"].mean().reset_index()
            industry_score.columns = ["industry", "avg_score"]
            industry_score = industry_score.sort_values("avg_score", ascending=False) if len(industry_score) > 0 and "avg_score" in industry_score.columns else industry_score
            fig2 = px.bar(industry_score, x="industry", y="avg_score",
                title="Avg ICP Score by Industry",
                color="avg_score",
                color_continuous_scale=["#1A1D2E", "#00C48C"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color":"white"})
            st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)

        with c3:
            # Lead volume by month
            df["month"] = pd.to_datetime(df["date_added"]).dt.to_period("M").astype(str)
            monthly = df.groupby("month").size().reset_index(name="leads")
            fig3 = px.line(monthly, x="month", y="leads",
                title="Lead Volume by Month",
                color_discrete_sequence=["#00C48C"])
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color":"white"})
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            # Hot leads by title
            title_hot = df[df["status"]=="hot"].groupby("title").size().reset_index(name="hot_leads")
            title_hot = title_hot.sort_values("hot_leads", ascending=False).head(8)
            fig4 = px.bar(title_hot, x="hot_leads", y="title",
                orientation="h",
                title="Hot Leads by Job Title",
                color_discrete_sequence=["#00C48C"])
            fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color":"white"})
            st.plotly_chart(fig4, use_container_width=True)

        st.divider()
        st.subheader("Source Performance Breakdown")
        source_perf = df.groupby("source").agg(
            total=("status", "count"),
            hot=("status", lambda x: (x=="hot").sum()),
            warm=("status", lambda x: (x=="warm").sum()),
            cold=("status", lambda x: (x=="cold").sum()),
            avg_score=("icp_score", "mean")
        ).reset_index()
        source_perf["hot_rate"] = (source_perf["hot"] / source_perf["total"] * 100).round(1)
        source_perf["avg_score"] = source_perf["avg_score"].round(1)
        source_perf = source_perf.sort_values("hot_rate", ascending=False)
        st.dataframe(source_perf, use_container_width=True)
with tab_decay:
    from datetime import datetime
    st.header(" Lead Decay Alerts")
    st.caption("Leads going cold = revenue at risk. Act before they die.")

    df["date_added"] = pd.to_datetime(df["date_added"])
    df["days_inactive"] = (datetime.today() - df["date_added"]).dt.days

    def decay_label(row):
        if row["status"] == "cold":
            return "Already Cold"
        elif row["days_inactive"] > 90:
            return " Critical"
        elif row["days_inactive"] > 60:
            return " High Risk"
        elif row["days_inactive"] > 30:
            return " Watch"
        else:
            return " Active"

    df = df.copy()
    df["decay_status"] = df.apply(decay_label, axis=1)

    avg_deal_d = st.sidebar.number_input("Avg Deal Size ($)", value=5000, key="decay_deal")
    hot_conv_d = st.sidebar.number_input("Hot Close Rate (%)", value=40, key="decay_hot") / 100
    warm_conv_d = st.sidebar.number_input("Warm Close Rate (%)", value=20, key="decay_warm") / 100

    at_risk = df[df["decay_status"].isin([" Critical", " High Risk"])]
    hot_risk = len(at_risk[at_risk["status"] == "hot"])
    warm_risk = len(at_risk[at_risk["status"] == "warm"])
    revenue_at_risk = (hot_risk * hot_conv_d + warm_risk * warm_conv_d) * avg_deal_d

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(" Critical", len(df[df["decay_status"] == " Critical"]))
    col2.metric(" High Risk", len(df[df["decay_status"] == " High Risk"]))
    col3.metric(" Watch", len(df[df["decay_status"] == " Watch"]))
    col4.metric(" Revenue at Risk", f"${revenue_at_risk:,.0f}")

    st.divider()

    decay_counts = df["decay_status"].value_counts().reset_index()
    decay_counts.columns = ["Decay Status", "Count"]
    fig_decay = px.bar(
        decay_counts, x="Decay Status", y="Count", color="Decay Status",
        color_discrete_map={
            " Critical": "#FF4444",
            " High Risk": "#FF8C00",
            " Watch": "#FFD700",
            " Active": "#00C48C",
            "Already Cold": "#555555"
        },
        title="Lead Decay Distribution"
    )
    fig_decay.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"})
    st.plotly_chart(fig_decay, use_container_width=True)

    st.subheader(" Leads Needing Immediate Action")
    urgency_filter = st.selectbox("Filter by urgency", ["All At-Risk", " Critical Only", " High Risk Only"])

    if urgency_filter == " Critical Only":
        show_df = df[df["decay_status"] == " Critical"]
    elif urgency_filter == " High Risk Only":
        show_df = df[df["decay_status"] == " High Risk"]
    else:
        show_df = at_risk

    st.dataframe(
        show_df[["icp_score", "status", "source", "days_inactive", "decay_status", "date_added"]]
        .sort_values("days_inactive", ascending=False),
        use_container_width=True
    )
    st.caption(f" ${revenue_at_risk:,.0f} in pipeline at risk from {len(at_risk)} decaying leads.")
with tab_brief:
    st.header("Daily GTM Brief")
    st.caption("AI-generated action plan based on your live pipeline.")

    from datetime import datetime
    import anthropic

    if st.button("Generate Today's Brief"):
        with st.spinner("Analyzing pipeline..."):

            total = len(df)
            hot = len(df[df["status"] == "hot"])
            warm = len(df[df["status"] == "warm"])
            cold = len(df[df["status"] == "cold"])

            df["date_added"] = pd.to_datetime(df["date_added"])
            df["days_inactive"] = (datetime.today() - df["date_added"]).dt.days
            critical = len(df[(df["days_inactive"] > 90) & (df["status"] != "cold")])
            high_risk = len(df[(df["days_inactive"] > 60) & (df["status"] != "cold")])

            top_source = df[df["status"] == "hot"]["source"].value_counts().idxmax()
            avg_icp = round(df["icp_score"].mean(), 1)

            summary = f"""
Pipeline snapshot as of today:
- Total leads: {total}
- Hot leads: {hot}
- Warm leads: {warm}
- Cold leads: {cold}
- Critical decay (90+ days inactive): {critical}
- High risk decay (60+ days inactive): {high_risk}
- Top source for hot leads: {top_source}
- Average ICP score: {avg_icp}

You are a senior GTM strategist. Based on this pipeline data, generate a concise daily sales brief with exactly 5 prioritized action items the sales team should take today. Be specific, direct, and data-driven. No fluff. No emojis. Format as a numbered list.
"""

            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": summary}]
            )

            brief = message.content[0].text
            st.subheader("Today's Action Plan")
            st.markdown(brief)
            st.caption(f"Generated on {datetime.today().strftime('%B %d, %Y')}")
with tab_intel:
    st.header("Account Intelligence")
    st.caption("AI-generated research on any company in your pipeline.")

    import anthropic

    companies = df["source"].unique().tolist()

    col_a, col_b = st.columns(2)
    with col_a:
        selected_status = st.selectbox("Filter by status", ["All", "hot", "warm", "cold"], key="intel_status")

    if selected_status != "All":
        filtered_intel = df[df["status"] == selected_status]
    else:
        filtered_intel = df

    company_options = filtered_intel.index.tolist()
    selected_lead = st.selectbox(
        "Select a lead to research",
        company_options,
        format_func=lambda x: f"Lead #{x} | {df.loc[x, 'source']} | {df.loc[x, 'status']} | Score: {df.loc[x, 'icp_score']}",
        key="intel_lead"
    )

    if st.button("Generate Account Intelligence"):
        lead = df.loc[selected_lead]

        prompt = f"""
You are a senior B2B sales strategist preparing a rep for a sales call.

Here is what we know about this account:
- Lead source: {lead['source']}
- Company size: {lead['employees']} employees
- Revenue range: {lead['revenue']}
- Current status: {lead['status']}
- ICP Score: {lead['icp_score']}
- Days in pipeline: {lead['days_inactive']}

Generate a structured account intelligence brief with these exact sections:

1. COMPANY PROFILE
What type of company this likely is based on size and revenue.

2. BUDGET ESTIMATE
What budget range they likely have for solutions like ours.

3. DECISION MAKER
Who the likely decision maker is by title and what they care about.

4. BEST PITCH ANGLE
The single strongest angle to open with on a call.

5. RISK FACTORS
Top 2 reasons this deal might not close.

6. RECOMMENDED NEXT ACTION
One specific action to take in the next 48 hours.

Be specific, direct, and concise. No emojis. No fluff.
"""

        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

        with st.spinner("Generating account intelligence..."):
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )

        intel = message.content[0].text

        st.divider()
        st.subheader(f"Account Brief — Lead #{selected_lead}")
        st.markdown(intel)
        st.caption(f"ICP Score: {lead['icp_score']} | Status: {lead['status']} | Source: {lead['source']}")
