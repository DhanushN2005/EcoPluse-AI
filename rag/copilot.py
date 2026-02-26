from openai import OpenAI
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY
from .prompts import SYSTEM_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_copilot(query, current_metrics, active_alerts):
    """Interacts with the LLM to provide environmental insights."""
    context = f"""
    Current Metrics: {current_metrics}
    Active Alerts: {active_alerts}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context: {context}\n\nUser Question: {query}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        if "429" in str(e) or "insufficient_quota" in str(e):
            return f"""[DEMO MODE - API Quota Exceeded]
Based on the live data (AQI: {current_metrics.get('aqi')}), the air quality is currently {current_metrics.get('severity')}. 
The primary driver is {current_metrics.get('attribution', {}).get('traffic')}% traffic density. 
Recommendation: Implement local traffic restrictions in central zones and advise sensitive groups to remain indoors."""
        return f"Error contacting Copilot: {str(e)}"
