from fastapi import FastAPI
from app.routers import leads

app = FastAPI(
    title="RevenueOS API",
    description="AI-powered GTM Revenue Operating System",
    version="1.0.0"
)

app.include_router(leads.router, prefix="/api/v1", tags=["Leads"])

@app.get("/")
def health_check():
    return {"status": "RevenueOS is running", "version": "1.0.0"}
