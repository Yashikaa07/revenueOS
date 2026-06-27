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

st.set_page_config(page_title="RevenueOS", page_icon="🚀", layout="wide")

st.title("🚀 RevenueOS")
st.caption("AI-powered lead enrichment, scoring, and outreach automation")

# Load dataset
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'leads_dataset.csv')
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_data()

# Sidebar
with st.sidebar:
    st.header("➕ Add New Lead")
    first_name = st.text_input("First Name", "Sarah")
    last_name = st.text_input("Last Name", "Chen")
    email = st.text_input("Email", "sarah@techflow.io")
    company = st.text_input("Company", "TechFlow Inc")
    job_title = st.text_input("Job Title", "VP of Sales")
    source = st.selectbox("Source", ["website", "linkedin", "referral", "event"])
    analyze = st.button("🔍 Analyze Lead", use_container_width=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Pipeline Dashboard", "🤖 AI Assistant", "📋 All Leads"])

# ── TAB 1: Pipeline Dashboard ──
with tab1:
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Leads", len(df))
        col2.metric("🔥 Hot", len(df[df['status']=='hot']))
        col3.metric("🌡️ Warm", len(df[df['status']=='warm']))
        col4.metric("❄️ Cold", len(df[df['status']=='cold']))

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.histogram(df, x='icp_score', color='status',
                title='ICP Score Distribution',
                color_discrete_map={'hot':'#ff4b4b','warm':'#ffa500','cold':'#4b9dff'})
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            fig2 = px.bar(df['industry'].value_counts().reset_index(),
                x='industry', y='count', title='Leads by Industry',
                color_discrete_sequence=['#7c83fd'])
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
            st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            fig3 = px.pie(df, names='source', title='Lead Sources',
                color_discrete_sequence=['#ff4b4b','#ffa500','#7c83fd','#4b9dff','#00cc96'])
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            trend = df.groupby('date_added').size().reset_index(name='leads')
            fig4 = px.line(trend, x='date_added', y='leads', title='Leads Over Time',
                color_discrete_sequence=['#7c83fd'])
            fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
            st.plotly_chart(fig4, use_container_width=True)

    if analyze:
        with st.spinner("Running AI analysis..."):
            lead_data = {
                "first_name": first_name, "last_name": last_name,
                "email": email, "company": company,
                "job_title": job_title, "source": source
            }
            company_data = enrich_company(company)
            scoring = score_lead(lead_data, company_data)
            grade = scoring['grade']
            score = scoring['score']

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("ICP Score", f"{score}/100")
            col2.metric("Grade", f"{'🔥' if grade=='HOT' else '🌡️' if grade=='WARM' else '❄️'} {grade}")
            col3.metric("Industry", company_data.get('industry', 'Unknown'))
            col4.metric("Employees", company_data.get('employees', 0))
            col5.metric("Revenue", company_data.get('revenue', 'Unknown'))

            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("👤 Lead & Company Info")
                st.write(f"**Name:** {first_name} {last_name}")
                st.write(f"**Title:** {job_title}")
                st.write(f"**Company:** {company}")
                st.write(f"**Industry:** {company_data.get('industry', 'Unknown')}")
                st.write(f"**Location:** {company_data.get('location', 'Unknown')}")
                st.write(f"**Revenue:** {company_data.get('revenue', 'Unknown')}")

                st.subheader("📊 Score Breakdown")
                breakdown = scoring.get('breakdown', {})
                if breakdown:
                    fig = px.bar(
                        x=list(breakdown.keys()),
                        y=list(breakdown.values()),
                        color_discrete_sequence=['#7c83fd']
                    )
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("✉️ AI Generated Email")
                if grade == "HOT":
                    with st.spinner("Claude is writing your email..."):
                        email_content = generate_email(lead_data, company_data, scoring)
                    st.text_area("Generated Email", value=email_content, height=280)
                    st.success("✅ Email generated by Claude AI")
                    st.download_button("📥 Download Email", email_content,
                        file_name=f"email_{first_name}_{last_name}.txt")
                    if st.button("📧 Send Email via Gmail"):
                        success, msg = send_email(email, f"Quick note for {first_name}", email_content)
                        if success:
                            st.success("✅ Email sent to " + email)
                        else:
                            st.error("❌ Failed: " + msg)
                else:
                    st.info(f"Score is {score}/100 — AI email triggers at 70+")

# ── TAB 2: AI Assistant ──
with tab2:
    st.subheader("🤖 Ask Anything About Your Pipeline")
    st.caption("Powered by Claude AI — ask about leads, scores, industries, trends")

    if df.empty:
        st.warning("No dataset loaded. Generate leads first.")
    else:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Show chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Suggested questions
        st.write("**Try asking:**")
        cols = st.columns(3)
        suggestions = [
            "Which industry has the most hot leads?",
            "Who should I contact first this week?",
            "What's my average ICP score?",
            "Which lead source converts best?",
            "How many leads came from LinkedIn?",
            "Show me top 5 leads to prioritize"
        ]
        for i, s in enumerate(suggestions):
            if cols[i % 3].button(s, key=f"sug_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": s})
                with st.spinner("Thinking..."):
                    answer = ask_pipeline(s, df)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()

        # Chat input
        question = st.chat_input("Ask about your pipeline...")
        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Thinking..."):
                answer = ask_pipeline(question, df)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

# ── TAB 3: All Leads ──
with tab3:
    st.subheader("📋 Full Lead Database")
    if df.empty:
        st.warning("No leads found.")
    else:
        col1, col2, col3 = st.columns(3)
        status_filter = col1.selectbox("Filter by Status", ["All", "hot", "warm", "cold"])
        industry_filter = col2.selectbox("Filter by Industry", ["All"] + sorted(df['industry'].unique().tolist()))
        source_filter = col3.selectbox("Filter by Source", ["All"] + sorted(df['source'].unique().tolist()))

        filtered = df.copy()
        if status_filter != "All":
            filtered = filtered[filtered['status'] == status_filter]
        if industry_filter != "All":
            filtered = filtered[filtered['industry'] == industry_filter]
        if source_filter != "All":
            filtered = filtered[filtered['source'] == source_filter]

        st.write(f"Showing **{len(filtered)}** leads")
        st.dataframe(filtered.sort_values('icp_score', ascending=False), use_container_width=True)

        csv = filtered.to_csv(index=False)
        st.download_button("📥 Export CSV", csv, file_name="filtered_leads.csv", mime="text/csv")
