def score_lead(lead_data: dict, company_data: dict) -> dict:
    score = 0
    reasons = []

    # Industry scoring
    industry = company_data.get("industry", "").lower()
    if industry in ["saas", "ai/ml"]:
        score += 30
        reasons.append("High-value industry (SaaS/AI)")
    elif industry in ["marketing tech", "fintech"]:
        score += 20
        reasons.append("Good industry match")
    else:
        reasons.append("Industry not in ICP")

    # Company size scoring
    employees = company_data.get("employee_count", 0)
    if 50 <= employees <= 500:
        score += 25
        reasons.append("Ideal company size (50-500 employees)")
    elif 10 <= employees < 50:
        score += 10
        reasons.append("Small company — lower priority")
    else:
        reasons.append("Company size outside ICP range")

    # Job title scoring
    title = lead_data.get("job_title", "").lower()
    if any(t in title for t in ["ceo", "cto", "vp", "head", "director"]):
        score += 30
        reasons.append("Decision maker title")
    elif any(t in title for t in ["manager", "lead"]):
        score += 15
        reasons.append("Influencer title")
    else:
        reasons.append("Title not a decision maker")

    # Source scoring
    source = lead_data.get("source", "").lower()
    if source in ["referral", "event"]:
        score += 15
        reasons.append("High-intent source")
    elif source == "website":
        score += 10
        reasons.append("Website lead")

    # Grade
    if score >= 40:
        grade = "HOT"
    elif score >= 40:
        grade = "WARM"
    else:
        grade = "COLD"

    return {
        "score": score,
        "grade": grade,
        "reasons": reasons
    }
