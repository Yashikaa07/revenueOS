import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_slack_alert(lead_data: dict, scoring: dict, company_data: dict):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("No Slack webhook URL found")
        return

    grade = scoring.get("grade", "UNKNOWN")
    score = scoring.get("score", 0)
    
    emoji = "🔥" if grade == "HOT" else "⚡" if grade == "WARM" else "❄️"

    message = {
        "text": f"{emoji} *New {grade} Lead — {score}/100*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *New {grade} Lead Detected!*\n*Score: {score}/100*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Name:*\n{lead_data.get('first_name')} {lead_data.get('last_name')}"},
                    {"type": "mrkdwn", "text": f"*Title:*\n{lead_data.get('job_title')}"},
                    {"type": "mrkdwn", "text": f"*Company:*\n{lead_data.get('company')}"},
                    {"type": "mrkdwn", "text": f"*Industry:*\n{company_data.get('industry')}"},
                    {"type": "mrkdwn", "text": f"*Employees:*\n{company_data.get('employee_count')}"},
                    {"type": "mrkdwn", "text": f"*Revenue:*\n{company_data.get('annual_revenue')}"}
                ]
            }
        ]
    }

    response = requests.post(webhook_url, json=message)
    
    if response.status_code == 200:
        print("  Slack alert sent!")
    else:
        print(f"  Slack error: {response.status_code}")
        