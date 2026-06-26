import streamlit as st
import sys
import os
import plotly.graph_objects as go
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.enrichment import enrich_company
from app.modules.icp_scoring import score_lead
from app.modules.email_gen import generate_email
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="RevenueOS Dashboard", page_icon="🚀", layout="wide")

st.title("🚀 RevenueOS — GTM Revenue Operating System")
st.caption("AI-powered lead enrichment, scoring, and outreach automation")
st.markdown("---")

st.sidebar.header("➕ Add New Lead")
first_name = st.sidebar.text_input("First Name", "Sarah")
last_name = st.sidebar.text_input("Last Name", "Chen")
email = st.sidebar.text_input("Email", "sarah@techflow.io")
company = st.sidebar.text_input("Company", "TechFlow Inc")
job_title = st.sidebar.text_input("Job Title", "VP of Sales")
source = st.sidebar.selectbox("Source", ["website", "linkedin", "referral", "event"])

analyze = st.sidebar.button("🔍 Analyze Lead", use_container_width=True)

if analyze:
    with st.spinner("Running AI analysis..."):
        lead_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "company": company,
            "job_title": job_title,
            "source": source
        }

        company_data = enrich_company(company)
        scoring = score_lead(lead_data, company_data)
        grade = scoring['grade']
        score = scoring['score']

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("ICP Score", f"{score}/100")
        with col2:
            emoji = "🔥" if grade == "HOT" else "⚡" if grade == "WARM" else "❄️"
            st.metric("Grade", f"{emoji} {grade}")
        with col3:
            st.metric("Industry", company_data['industry'])
        with col4:
            st.metric("Employees", company_data['employee_count'])
        with col5:
            st.metric("Revenue", company_data['annual_revenue'])

        st.markdown("---")

        col1, col2 = st.columns([1, 1])

        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={'text': "ICP Score", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#ff4b4b" if score >= 70 else "#ffa500" if score >= 40 else "#4b9dff"},
                    'steps': [
                        {'range': [0, 40], 'color': "#1e2130"},
                        {'range': [40, 70], 'color': "#2d3250"},
                        {'range': [70, 100], 'color': "#3d4170"}
                    ],
                }
            ))
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("👤 Lead & Company Info")
            st.write(f"**Name:** {first_name} {last_name}")
            st.write(f"**Title:** {job_title}")
            st.write(f"**Company:** {company}")
            st.write(f"**Industry:** {company_data['industry']}")
            st.write(f"**Location:** {company_data['location']}")
            st.write(f"**Revenue:** {company_data['annual_revenue']}")

            st.markdown("---")
            st.subheader("📊 Score Breakdown")
            categories = ['Industry', 'Company Size', 'Job Title', 'Lead Source']
            values = [30, 25, 30, 15]
            fig2 = px.bar(x=values, y=categories, orientation='h',
                         color_discrete_sequence=['#ff4b4b'])
            fig2.update_layout(height=200, paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)', font={'color': 'white'},
                              showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("✅ Scoring Reasons")
            for reason in scoring['reasons']:
                st.success(f"✓ {reason}")

            labels = ['Industry Match', 'Company Size', 'Title Authority', 'Source Quality']
            values_pie = [30, 25, 30, 15]
            fig3 = px.pie(values=values_pie, names=labels,
                         color_discrete_sequence=['#ff4b4b', '#ffa500', '#7c83fd', '#4b9dff'],
                         hole=0.4)
            fig3.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)',
                              font={'color': 'white'}, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig3, use_container_width=True)

        with col2:
            st.subheader("✉️ AI Generated Email")
            if grade == "HOT":
                with st.spinner("Claude is writing your email..."):
                    email_content = generate_email(lead_data, company_data, scoring)
                    st.text_area("Generated Email", value=email_content, height=280)
                    st.success("✅ Email generated by Claude AI")
                    st.download_button("📥 Download Email", email_content,
                                      file_name=f"email_{first_name}_{last_name}.txt")
            else:
                st.info(f"Score is {score}/100 — AI email triggers at 70+")
                