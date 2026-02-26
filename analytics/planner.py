from openai import OpenAI
import os
import sys

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ecopulse_ai.config import OPENAI_API_KEY
from ecopulse_ai.analytics.health_score import calculate_composite_health

client = OpenAI(api_key=OPENAI_API_KEY)

PLANNER_PROMPT = """
You are the EcoPulse AI Smart City Operations Planner. 
Your task is to generate a detailed, AI-driven operational plan called "Today's Air Action Plan" based on environmental data.

Data Provided:
- Live AQI
- Short-term Forecast (Expected AQI)
- Active Alerts
- Environmental Health Score
- Risk Probability

Your response MUST be in JSON format with the following structure:
{
  "summary": "Short 1-sentence status snapshot",
  "recommendations": [
    {"title": "Action Title", "description": "Details", "impact": "High/Medium/Low"}
  ],
  "projected_impacts": [
    {"metric": "AQI Reduction", "value": "e.g. 15%"},
    {"metric": "Health Risk Improvement", "value": "e.g. 22%"}
  ],
  "operational_readiness": "Ready/Partial/Standby"
}

Focus on city-wide actions: adjusting outdoor activity timing, encouraging remote work, limiting industrial output, or issuing public advisories.
Be specific and professional.
"""

def generate_action_plan(latest_metrics, forecast, alerts):
    health_score = calculate_composite_health(
        latest_metrics.get('aqi', 0),
        latest_metrics.get('co2', 0),
        latest_metrics.get('pm25', 0),
        latest_metrics.get('humidity', 50)
    )
    
    # Calculate a mock risk probability based on AQI and forecast
    risk_prob = min(95, (latest_metrics.get('aqi', 0) / 300) * 100 + (10 if forecast > latest_metrics.get('aqi', 0) else -5))
    risk_prob = round(max(5, risk_prob), 1)

    context = f"""
    Live AQI: {latest_metrics.get('aqi')}
    Forecast: {forecast}
    Alerts: {alerts}
    Health Score: {health_score}
    Risk Probability: {risk_prob}%
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": PLANNER_PROMPT},
                {"role": "user", "content": f"Generate the action plan for this context: {context}"}
            ],
            response_format={ "type": "json_object" },
            temperature=0.7
        )
        import json
        plan = json.loads(response.choices[0].message.content)
        plan['health_score'] = health_score
        plan['risk_prob'] = risk_prob
        plan['metrics'] = latest_metrics
        return plan
    except Exception as e:
        # Fallback for demo or error
        return {
            "summary": "Air quality is deteriorating; proactive measures required.",
            "recommendations": [
                {"title": "Commute Advisory", "description": "Encourage remote work for non-essential sectors to reduce peak traffic emissions.", "impact": "High"},
                {"title": "Industrial Regulation", "description": "Implement Stage 1 output reduction for high-emission plants in the industrial belt.", "impact": "Medium"},
                {"title": "Public Safety", "description": "Postpone all outdoor school activities and city marathons.", "impact": "High"}
            ],
            "projected_impacts": [
                {"metric": "Expected AQI Reduction", "value": "12-18%"},
                {"metric": "Health Risk Improvement", "value": "25%"}
            ],
            "operational_readiness": "Partial",
            "health_score": health_score,
            "risk_prob": risk_prob,
            "metrics": latest_metrics
        }
