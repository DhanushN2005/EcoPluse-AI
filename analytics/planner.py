import os
import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from ecopulse_ai.config import OPENAI_API_KEY
from ecopulse_ai.analytics.health_score import calculate_composite_health

logger = logging.getLogger("Analytics-Planner")

# Initialize OpenAI client with project-wide key
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

def generate_action_plan(latest_metrics: Dict[str, Any], forecast: float, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Orchestrates the generation of an AI-driven operational plan using the Greenhouse Gas Health engine.
    
    Args:
        latest_metrics (Dict[str, Any]): The latest sensor telemetry.
        forecast (float): The projected AQI for the next period.
        alerts (List[Dict[str, Any]]): Currently active system alerts.
        
    Returns:
        Dict[str, Any]: A structured action plan from the LLM or a safe fallback.
    """
    health_score = calculate_composite_health(
        latest_metrics.get('aqi', 0),
        latest_metrics.get('co2', 0),
        latest_metrics.get('pm25', 0),
        latest_metrics.get('humidity', 50)
    )
    
    # Calculate a heuristic risk probability based on current levels and trends
    current_aqi = latest_metrics.get('aqi', 0)
    risk_prob = min(95, (current_aqi / 300) * 100 + (10 if forecast > current_aqi else -5))
    risk_prob = round(max(5, risk_prob), 1)

    context = f"""
    Live AQI: {current_aqi}
    Forecasted AQI: {forecast}
    System Alerts: {alerts}
    Environmental Health Score: {health_score}
    Calculated Risk Probability: {risk_prob}%
    """

    try:
        logger.info("Requesting operational action plan from AI engine...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": PLANNER_PROMPT},
                {"role": "user", "content": f"Generate the action plan for this context: {context}"}
            ],
            response_format={ "type": "json_object" },
            temperature=0.7,
            timeout=10.0
        )
        
        plan = json.loads(response.choices[0].message.content)
        
        # Enforce consistent structure
        plan.update({
            'health_score': health_score,
            'risk_prob': risk_prob,
            'metrics': latest_metrics
        })
        return plan
        
    except Exception as e:
        logger.warning(f"AI Plan Generation failed (using static fallback): {e}")
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
