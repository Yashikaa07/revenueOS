def enrich_company(company_name: str) -> dict:
    mock_database = {
        "techflow inc": {
            "industry": "SaaS",
            "employee_count": 150,
            "annual_revenue": "$10M-$50M",
            "location": "San Francisco, CA",
            "founded": 2018,
            "description": "B2B sales automation software"
        },
        "growthbase": {
            "industry": "Marketing Tech",
            "employee_count": 80,
            "annual_revenue": "$5M-$10M",
            "location": "New York, NY",
            "founded": 2019,
            "description": "Growth analytics platform"
        },
        "scalepath ai": {
            "industry": "AI/ML",
            "employee_count": 25,
            "annual_revenue": "$1M-$5M",
            "location": "Austin, TX",
            "founded": 2022,
            "description": "AI-powered revenue tools"
        }
    }

    key = company_name.lower().strip()
    result = mock_database.get(key, {
        "industry": "Unknown",
        "employee_count": 0,
        "annual_revenue": "Unknown",
        "location": "Unknown",
        "founded": None,
        "description": "No data available"
    })

    result["company_name"] = company_name
    return result