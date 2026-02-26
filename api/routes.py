import os
import sys
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from flask import (
    Blueprint, 
    render_template, 
    jsonify, 
    request, 
    redirect, 
    url_for, 
    flash, 
    send_file,
    Response
)
from flask_login import login_user, logout_user, login_required, current_user

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ecopulse_ai.config import STREAM_HOST, STREAM_PORT, REPORT_DIR
from ecopulse_ai.analytics.alerts import get_alert_status
from ecopulse_ai.analytics.prediction import get_aqi_forecast
from ecopulse_ai.rag.copilot import ask_copilot
from .models import User

# Configure logging
logger = logging.getLogger("Web-Routes")

main_bp = Blueprint('main', __name__)

@main_bp.route('/login', methods=['GET', 'POST'])
def login() -> Union[Response, str]:
    """Handles user authentication and session management."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.find_by_email(email)
        if user and user.verify_password(password):
            login_user(user)
            logger.info(f"User {email} logged in successfully.")
            return redirect(url_for('main.dashboard'))
        else:
            logger.warning(f"Failed login attempt for email: {email}")
            flash('Invalid email or password.')
    
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout() -> Response:
    """Terminates user session."""
    logger.info(f"User {current_user.email} logged out.")
    logout_user()
    return redirect(url_for('main.login'))

@main_bp.route('/')
@login_required
def dashboard() -> str:
    """Serves the main environmental dashboard."""
    return render_template('dashboard.html')

@main_bp.route('/analytics')
@login_required
def analytics() -> str:
    """Serves the complex analytics view."""
    return render_template('analytics.html')

@main_bp.route('/copilot')
@login_required
def copilot() -> str:
    """Serves the AI Copilot chat interface."""
    return render_template('copilot.html')

@main_bp.route('/governance')
@login_required
def governance() -> str:
    """Serves the environmental governance and strategy view."""
    return render_template('governance.html')

@main_bp.route('/national')
@login_required
def national() -> str:
    """Serves the national-level heatmap view."""
    return render_template('national.html')

@main_bp.route('/archives')
@login_required
def archives() -> str:
    """Serves archived environmental incident records."""
    return render_template('archives.html')

@main_bp.route('/reports')
@login_required
def reports() -> str:
    """Serves the report generation and export dashboard."""
    return render_template('reports.html')

@main_bp.route('/action-plan')
@login_required
def action_plan() -> Union[Response, str]:
    """Generates an AI-driven action plan based on current health status."""
    try:
        response = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics", timeout=5)
        data = response.json()
        latest = data[-1] if data else {}
        
        history = [d['aqi'] for d in data[-20:]] if len(data) >= 5 else [0]*5
        forecast = get_aqi_forecast(history)
        alerts = get_alert_status(latest)
        
        from ecopulse_ai.analytics.planner import generate_action_plan
        plan = generate_action_plan(latest, forecast, alerts)
        
        return render_template('action_plan.html', plan=plan)
    except Exception as e:
        logger.error(f"Error generating action plan: {e}")
        return redirect(url_for('main.dashboard'))

@main_bp.route('/api/national')
@login_required
def get_national() -> Response:
    """Proxies national metrics from the streaming engine."""
    try:
        response = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/national_metrics", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Failed to fetch national metrics: {e}")
        return jsonify([])

@main_bp.route('/api/districts')
@login_required
def get_districts() -> Response:
    """Proxies district-level comparison data from the analytics engine."""
    try:
        response = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/district_comparison", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Failed to fetch district metrics: {e}")
        return jsonify([])

@main_bp.route('/reports/mayor-brief')
@login_required
def export_mayor_brief() -> Response:
    """Generates and serves a 'Mayor-Level' PDF briefing report."""
    try:
        resp = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics", timeout=5)
        data = resp.json()
    except Exception as e:
        logger.error(f"Data fetch failed for mayor brief: {e}")
        data = []
        
    filename = f"mayor_briefing_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    report_path = os.path.join(REPORT_DIR, filename)
    
    from ecopulse_ai.reports.generator import generate_mayor_briefing
    generate_mayor_briefing(data, report_path)
    
    return send_file(report_path, as_attachment=True)

@main_bp.route('/api/metrics')
@login_required
def get_metrics() -> Response:
    """API endpoint for fetching real-time environmental metrics and forecasts."""
    try:
        response = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics", params=request.args, timeout=5)
        data = response.json()
        if not data:
            return jsonify({"error": "No data from Pathway"}), 404
        
        latest = data[-1]
        alerts = get_alert_status(latest)
        history = [d['aqi'] for d in data[-20:]]
        forecast = get_aqi_forecast(history)
        
        return jsonify({
            "latest": latest,
            "alerts": alerts,
            "forecast": forecast,
            "history": data[-50:]
        })
    except Exception as e:
        logger.error(f"Metrics Proxy Error: {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/chat', methods=['POST'])
@login_required
def chat() -> Response:
    """Integrates the LLM-powered Climate Copilot with real-time analytics."""
    body = request.json
    query = body.get('query')
    
    try:
        r = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics", timeout=5)
        latest = r.json()[-1] if r.json() else {}
        alerts = get_alert_status(latest)
        
        response_text = ask_copilot(query, latest, alerts)
        return jsonify({"response": response_text})
    except Exception as e:
        logger.error(f"Copilot logic error: {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/reports/export')
@login_required
def export_report() -> Response:
    """Generates and serves a full professional environmental health report."""
    try:
        resp = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics", timeout=5)
        data = resp.json()
    except Exception as e:
        logger.error(f"Data fetch failed for full report: {e}")
        data = []
        
    filename = f"ecopulse_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    report_path = os.path.join(REPORT_DIR, filename)
    
    from ecopulse_ai.reports.generator import generate_full_report
    generate_full_report(data, report_path)
    
    return send_file(report_path, as_attachment=True)
