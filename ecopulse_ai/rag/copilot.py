import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from ecopulse_ai.config import OPENAI_API_KEY
from .prompts import SYSTEM_PROMPT

logger = logging.getLogger("RAG-Copilot")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def ask_copilot(
    query: str, current_metrics: Dict[str, Any], active_alerts: List[Dict[str, Any]]
) -> str:
    """
    Interfaces with the OpenAI GPT-4o model to provide context-aware environmental insights.

    Args:
        query (str): The user's natural language question.
        current_metrics (Dict[str, Any]): The latest sensor data state.
        active_alerts (List[Dict[str, Any]]): Currently triggered system alerts.

    Returns:
        str: The AI's generated response or a graceful fallback message.
    """
    context = f"""
    Current Telemetry: {current_metrics}
    Active System Alerts: {active_alerts}
    """

    try:
        logger.info(f"Querying AI Copilot: '{query}'")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context: {context}\n\nUser Question: {query}"},
            ],
            temperature=0.7,
            timeout=15.0,
        )
        return str(response.choices[0].message.content)

    except Exception as e:
        err_msg = str(e)
        logger.error(f"Copilot API interaction failed: {err_msg}")

        # Specific fallback for quota issues (common in project demos)
        if "429" in err_msg or "insufficient_quota" in err_msg:
            logger.warning("Quota exceeded - using deterministic data-driven fallback.")
            aqi = current_metrics.get("aqi", "Unknown")
            severity = current_metrics.get("severity", "Stable")
            traffic_impact = current_metrics.get("attribution", {}).get("traffic", "N/A")

            return (
                f"[SIMULATION MODE] Based on real-time data (AQI: {aqi}), "
                f"the environmental state is '{severity}'. High traffic ({traffic_impact}%) is a major contributor. "
                "I recommend limiting travel in high-congestion zones."
            )

        return f"Service Temporary Unavailable: {err_msg}"
