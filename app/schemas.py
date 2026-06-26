from pydantic import BaseModel, EmailStr
from typing import Optional

class LeadInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    company: str
    job_title: str
    company_website: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = "manual"

class LeadResponse(BaseModel):
    message: str
    lead_id: str
    status: str