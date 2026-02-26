"""
EcoPulse AI Web Routing & Proxy Layer.
Orchestrates the interaction between the Flask frontend, the streaming analytics engine, 
and the AI reasoning services.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests
from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from ecopulse_ai.analytics.alerts import get_alert_status
from ecopulse_ai.analytics.prediction import get_aqi_forecast
from ecopulse_ai.config import REPORT_DIR, STREAM_HOST, STREAM_PORT
from ecopulse_ai.rag.copilot import ask_copilot

from .models import User

# Configure module-level logging
logger = logging.getLogger("Web-Routes")

main_bp = Blueprint("main", __name__)


# --- Helper Utilities (Modular Design) ---

def _fetch_streaming_data(endpoint: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Modular abstraction for fetching telemetry from the Pathway Analytics Engine.
    """
    url = f"http://{STREAM_HOST}:{STREAM_PORT}/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed telemetry fetch from {endpoint}: {e}")
        return []


def _generate_metric_package(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Enriches raw telemetry with forecasts and alert classifications for the UI.
    """
    if not data:
        return {"error": "Telemetry stream unavailable"}

    latest = data[-1]
    history = [d.get("aqi", 0) for d in data[-20:]]
    
    return {
        "latest": latest,
        "alerts": get_alert_status(latest),
        "forecast": get_aqi_forecast(history),
        "history": data[-50:],
    }


# --- Authentication Routes ---

@main_bp.route("/login", methods=["GET", "POST"])
def login() -> Union[Response, str]:
    """Handles secure user authentication and session establishment."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Robust input validation
        if not email or not password:
            flash("Please provide both email and password credentials.")
            return render_template("login.html")

        user = User.find_by_email(email)
        if user and user.verify_password(password):
            login_user(user)
            logger.info(f"Session established for user: {email}")
            return redirect(url_for("main.dashboard"))
        
        logger.warning(f"Unauthorized login attempt blocked for: {email}")
        flash("Invalid email or password.")

    return render_template("login.html")


@main_bp.route("/logout")
@login_required
def logout() -> Response:
    """Terminates the current user session securely."""
    logger.info(f"User {current_user.email} signed out.")
    logout_user()
    return redirect(url_for("main.login"))


# --- Dashboard & View Presentation ---

@main_bp.route("/")
@login_required
def dashboard() -> str:
    return render_template("dashboard.html")


@main_bp.route("/analytics")
@login_required
def analytics() -> str:
    return render_template("analytics.html")


@main_bp.route("/copilot")
@login_required
def copilot() -> str:
    return render_template("copilot.html")


@main_bp.route("/governance")
@login_required
def governance() -> str:
    return render_template("governance.html")


@main_bp.route("/national")
@login_required
def national() -> str:
    return render_template("national.html")


@main_bp.route("/reports")
@login_required
def reports() -> str:
    return render_template("reports.html")


@main_bp.route("/action-plan")
@login_required
def action_plan() -> Union[Response, str]:
    """Generates an AI-optimized municipal action plan."""
    data = _fetch_streaming_data("environmental_metrics")
    if not data:
        flash("Unable to generate plan: Real-time telemetry currently offline.")
        return redirect(url_for("main.dashboard"))

    latest = data[-1]
    history = [d.get("aqi", 0) for d in data[-20:]]
    forecast = get_aqi_forecast(history)
    alerts = get_alert_status(latest)

    from ecopulse_ai.analytics.planner import generate_action_plan
    plan = generate_action_plan(latest, forecast, alerts)
    
    return render_template("action_plan.html", plan=plan)


# --- Data & Proxy API Endpoints ---

@main_bp.route("/api/metrics")
@login_required
def get_metrics() -> Response:
    """Unified endpoint for telemetry, alerts, and forecasts."""
    data = _fetch_streaming_data("environmental_metrics", params=request.args)
    if not data:
        return jsonify({"error": "Service unavailable"}), 503
    
    package = _generate_metric_package(data)
    return jsonify(package)


@main_bp.route("/api/national")
@login_required
def get_national() -> Response:
    return jsonify(_fetch_streaming_data("national_metrics"))


@main_bp.route("/api/districts")
@login_required
def get_districts() -> Response:
    return jsonify(_fetch_streaming_data("district_comparison"))


@main_bp.route("/api/chat", methods=["POST"])
@login_required
def chat() -> Response:
    """Context-aware Copilot integration endpoint."""
    body = request.json or {}
    query = body.get("query")
    
    if not query:
        return jsonify({"error": "Query string is mandatory"}), 400

    data = _fetch_streaming_data("environmental_metrics")
    latest = data[-1] if data else {}
    alerts = get_alert_status(latest)

    response_text = ask_copilot(query, latest, alerts)
    return jsonify({"response": response_text})


# --- Document Generation & Exports ---

@main_bp.route("/reports/export")
@login_required
def export_report() -> Response:
    """Orchestrates the generation of a high-fidelity environmental audit."""
    data = _fetch_streaming_data("environmental_metrics")
    
    filename = f"ecopulse_audit_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    report_path = os.path.join(REPORT_DIR, filename)

    from ecopulse_ai.reports.generator import generate_full_report
    generate_full_report(data, report_path)

    return send_file(report_path, as_attachment=True)


@main_bp.route("/reports/mayor-brief")
@login_required
def export_mayor_brief() -> Response:
    """Orchestrates the generation of a strategic executive briefing."""
    data = _fetch_streaming_data("environmental_metrics")
    
    filename = f"mayor_briefing_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    report_path = os.path.join(REPORT_DIR, filename)

    from ecopulse_ai.reports.generator import generate_mayor_briefing
    generate_mayor_briefing(data, report_path)

    return send_file(report_path, as_attachment=True)
