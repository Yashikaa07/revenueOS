import csv, random, datetime

companies = ["Salesforce","HubSpot","Zendesk","Intercom","Drift","Gong","Outreach","Apollo","ZoomInfo","Clearbit","Mixpanel","Segment","Amplitude","Braze","Klaviyo","Marketo","Pardot","ActiveCampaign","Pipedrive","Monday.com"]
industries = ["SaaS","Fintech","Healthcare","E-commerce","Real Estate","Manufacturing","Consulting","Media","Logistics","EdTech"]
titles = ["VP of Sales","Head of Revenue","CEO","CMO","Director of Marketing","Sales Manager","Founder","CRO","Head of Growth","Business Development Manager"]
sources = ["linkedin","website","referral","cold_email","webinar","conference","inbound"]

rows = []
for i in range(500):
    score = random.randint(10,95)
    status = "hot" if score>=70 else "warm" if score>=45 else "cold"
    rows.append({
        "id": i+1,
        "first_name": random.choice(["James","Sarah","Michael","Emily","David","Jessica","Chris","Amanda","Ryan","Lisa"]),
        "last_name": random.choice(["Patel","Smith","Johnson","Williams","Brown","Davis","Miller","Wilson","Moore","Taylor"]),
        "company": random.choice(companies),
        "title": random.choice(titles),
        "industry": random.choice(industries),
        "employees": random.choice([10,50,100,250,500,1000,5000]),
        "revenue": random.choice(["<1M","1-10M","10-50M","50-100M","100M+"]),
        "source": random.choice(sources),
        "icp_score": score,
        "status": status,
        "date_added": (datetime.date(2024,1,1) + datetime.timedelta(days=random.randint(0,365))).isoformat()
    })

with open("data/leads_dataset.csv","w",newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Done — 500 leads generated")
