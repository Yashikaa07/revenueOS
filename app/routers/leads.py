from fastapi import APIRouter
from app.schemas import LeadInput, LeadResponse
from app.modules.enrichment import enrich_company
from app.modules.icp_scoring import score_lead
from app.modules.slack_alert import send_slack_alert
from app.modules.email_gen import generate_email
import uuid

router = APIRouter()

@router.post("/leads", response_model=LeadResponse)
async def capture_lead(lead: LeadInput):
    lead_id = str(uuid.uuid4())[:8]

    # Enrich company
    company_data = enrich_company(lead.company)

    # Score the lead
    lead_dict = lead.dict()
    scoring = score_lead(lead_dict, company_data)

    # Generate AI email for HOT leads
    email = ""
    if scoring["grade"] == "HOT":
        email = generate_email(lead_dict, company_data, scoring)
        print(f"\n AI Generated Email:")
        print(f"{email}")

    # Send Slack alert for HOT and WARM leads
    if scoring["grade"] in ["HOT", "WARM"]:
        send_slack_alert(lead_dict, scoring, company_data)

    print(f"\n New lead received:")
    print(f"  Name: {lead.first_name} {lead.last_name}")
    print(f"  Company: {lead.company}")
    print(f"  Score: {scoring['score']}/100")
    print(f"  Grade: {scoring['grade']}")

    return LeadResponse(
        message=f"Lead scored: {scoring['grade']} ({scoring['score']}/100)",
        lead_id=lead_id,
        status=scoring['grade']
    )
