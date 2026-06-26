import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

def generate_email(lead_data: dict, company_data: dict, scoring: dict) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

    prompt = f"""You are an expert B2B sales copywriter. Write a short, personalized cold email for this lead.

Lead Information:
- Name: {lead_data.get('first_name')} {lead_data.get('last_name')}
- Title: {lead_data.get('job_title')}
- Company: {lead_data.get('company')}
- Industry: {company_data.get('industry')}
- Company Size: {company_data.get('employee_count')} employees
- Revenue: {company_data.get('annual_revenue')}
- ICP Score: {scoring.get('score')}/100
- Score Reasons: {scoring.get('reasons')}

Rules:
- Maximum 4 sentences
- Mention their specific industry and company size
- Focus on one clear business problem we can solve
- End with a simple call to action
- Sound human, not robotic
- Do not use generic phrases like "I hope this email finds you well"

Write only the email body, no subject line.
"""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text
