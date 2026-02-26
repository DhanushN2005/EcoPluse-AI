from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
import requests
import os
import sys

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ecopulse_ai.config import STREAM_HOST, STREAM_PORT
from ecopulse_ai.analytics.alerts import get_alert_status
from ecopulse_ai.analytics.prediction import get_aqi_forecast
from ecopulse_ai.rag.copilot import ask_copilot

# Helper for User
from .models import User
from flask import send_file
from datetime import datetime
from ecopulse_ai.config import REPORT_DIR

main_bp = Blueprint('main', __name__)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.find_by_email(email)
        if user and user.verify_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password.')
    
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@main_bp.route('/copilot')
@login_required
def copilot():
    return render_template('copilot.html')

@main_bp.route('/governance')
@login_required
def governance():
    return render_template('governance.html')

@main_bp.route('/national')
@login_required
def national():
    return render_template('national.html')

@main_bp.route('/archives')
@login_required
def archives():
    return render_template('archives.html')

@main_bp.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@main_bp.route('/action-plan')
@login_required
def action_plan():
    try:
        # Fetch data for the plan
        response = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics")
        data = response.json()
        latest = data[-1] if data else {}
        
        # Get forecast
        history = [d['aqi'] for d in data[-20:]] if len(data) >= 5 else [0]*5
        forecast = get_aqi_forecast(history)
        
        # Get active alerts
        alerts = get_alert_status(latest)
        
        from ecopulse_ai.analytics.planner import generate_action_plan
        plan = generate_action_plan(latest, forecast, alerts)
        
        return render_template('action_plan.html', plan=plan)
    except Exception as e:
        print(f"Error generating action plan: {e}")
        return redirect(url_for('main.dashboard'))

@main_bp.route('/api/national')
@login_required
def get_national():
    try:
        response = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/national_metrics")
        return jsonify(response.json())
    except:
        return jsonify([])

@main_bp.route('/api/districts')
@login_required
def get_districts():
    try:
        response = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/district_comparison")
        return jsonify(response.json())
    except:
        return jsonify([])

@main_bp.route('/reports/mayor-brief')
@login_required
def export_mayor_brief():
    try:
        resp = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics")
        data = resp.json()
    except:
        data = []
        
    filename = f"mayor_briefing_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    report_path = os.path.join(REPORT_DIR, filename)
    
    from ecopulse_ai.reports.generator import generate_mayor_briefing
    generate_mayor_briefing(data, report_path)
    
    return send_file(report_path, as_attachment=True)

@main_bp.route('/api/metrics')
@login_required
def get_metrics():
    """Proxies metrics from Pathway."""
    try:
        response = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics", params=request.args)
        data = response.json()
        if not data:
            return jsonify({"error": "No data from Pathway"}), 404
        
        latest = data[-1]
        alerts = get_alert_status(latest)
        
        # Prediction
        history = [d['aqi'] for d in data[-20:]]
        forecast = get_aqi_forecast(history)
        
        return jsonify({
            "latest": latest,
            "alerts": alerts,
            "forecast": forecast,
            "history": data[-50:]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    body = request.json
    query = body.get('query')
    
    try:
        r = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics")
        latest = r.json()[-1] if r.json() else {}
        alerts = get_alert_status(latest)
        
        response = ask_copilot(query, latest, alerts)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/reports/export')
@login_required
def export_report():
    try:
        resp = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics")
        data = resp.json()
    except:
        data = []
        
    filename = f"ecopulse_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    report_path = os.path.join(REPORT_DIR, filename)
    
    from ecopulse_ai.reports.generator import generate_full_report
    generate_full_report(data, report_path)
    
    return send_file(report_path, as_attachment=True)
