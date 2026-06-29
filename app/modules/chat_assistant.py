import anthropic
import os
import pandas as pd

def get_pipeline_summary(df):
    summary = f"""
Total leads: {len(df)}
Hot leads: {len(df[df['status']=='hot'])}
Warm leads: {len(df[df['status']=='warm'])}
Cold leads: {len(df[df['status']=='cold'])}
Average ICP score: {df['icp_score'].mean():.1f}
Top industry: {df['industry'].value_counts().index[0]}
Top lead source: {df['source'].value_counts().index[0]}
Top company: {df['company'].value_counts().index[0]}
Industries breakdown: {df['industry'].value_counts().to_dict()}
Sources breakdown: {df['source'].value_counts().to_dict()}
Score distribution: min={df['icp_score'].min()}, max={df['icp_score'].max()}
"""
    return summary

def ask_pipeline(question, df):
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    summary = get_pipeline_summary(df)
    
    prompt = f"""You are a revenue operations analyst assistant. You have access to a B2B sales pipeline dataset.

Pipeline Data Summary:
{summary}

Sample of top 10 leads by ICP score:
{df.nlargest(10, 'icp_score')[['first_name','last_name','company','jobtitle','industry','icp_score','status','source']].to_string()}

Answer this question about the pipeline data:
{question}

Be specific, use numbers from the data, and give actionable insights. Keep it concise — 3-5 sentences max.
"""
    
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text
