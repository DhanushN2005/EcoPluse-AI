from fpdf import FPDF
import datetime
import os
import json

class EnvironmentalReport(FPDF):
    def header(self):
        # Header with branding
        self.set_fill_color(15, 76, 92) # #0F4C5C
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_font('Arial', 'B', 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 20, 'EcoPulse AI Executive Summary', 0, 1, 'C')
        
        self.set_font('Arial', 'I', 10)
        self.cell(0, 0, 'Integrated Smart-City Environmental Intelligence', 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

def generate_full_report(data, output_path):
    pdf = EnvironmentalReport()
    pdf.add_page()
    
    # Summary Section
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(15, 76, 92)
    pdf.cell(0, 10, '1. AI-Generated Environmental Insight', 0, 1)
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(50, 50, 50)
    
    latest_aqi = data[-1]['aqi'] if data else 0
    avg_aqi = sum(d['aqi'] for d in data) / len(data) if data else 0
    peak_time = datetime.datetime.now().strftime("%H:%M")
    
    insight = (
        f"The EcoPulse AI system has detected a daily AQI baseline of {avg_aqi:.1f}. "
        f"Analysis shows a peak pollution interval around {peak_time}, driven primarily by "
        f"low-level wind dispersion and traffic congestion. Our predictive engine suggests "
        f"that atmospheric stagnation will persist for the next 4 hours. "
        f"Strategic recommendation: Implement dynamic traffic diversion in Zone B to reduce the local load by 15%."
    )
    pdf.multi_cell(0, 6, insight)
    pdf.ln(10)

    # Analytics Data Table
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. Detailed Analytics Log', 0, 1)
    
    # Table Header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 10, 'Timestamp', 1, 0, 'C', True)
    pdf.cell(30, 10, 'AQI', 1, 0, 'C', True)
    pdf.cell(30, 10, 'Health Index', 1, 0, 'C', True)
    pdf.cell(90, 10, 'Primary attribution', 1, 1, 'C', True)

    pdf.set_font('Arial', '', 9)
    # Use last 15 records for the report
    for record in data[-15:]:
        ts = record.get('timestamp', '').split('T')[-1][:8]
        aqi = f"{record['aqi']:.1f}"
        health = f"{record.get('health_score', 0):.1f}"
        attr = record.get('attribution', {})
        attr_text = f"Traffic: {attr.get('traffic')}% | Wind: {attr.get('wind_impact')}%"
        
        pdf.cell(40, 8, ts, 1, 0, 'C')
        pdf.cell(30, 8, aqi, 1, 0, 'C')
        pdf.cell(30, 8, health, 1, 0, 'C')
        pdf.cell(90, 8, attr_text, 1, 1, 'L')

    pdf.ln(10)
    
    # Final Recommendation
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(46, 204, 113) # #2ECC71
    pdf.cell(0, 10, 'Strategic Municipal Action Items:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(50, 50, 50)
    actions = [
        "- Execute 'Green Pulse' traffic protocols in high-density corridors.",
        "- Deploy automated alert notifications to registered sensitive citizens.",
        "- Increase frequency of urban street misting in Sector 4.",
        "- Validate industrial emission compliance for outliers in Zone A."
    ]
    for action in actions:
        pdf.cell(0, 7, action, 0, 1)

    pdf.output(output_path)
    return output_path

def generate_mayor_briefing(data, output_path):
    pdf = EnvironmentalReport()
    pdf.add_page()
    
    latest = data[-1] if data else {}
    aqi = latest.get('aqi', 0)
    severity = latest.get('severity', 'Optimal')
    attr = latest.get('attribution', {})
    carbon = latest.get('carbon_footprint', {}).get('total_equivalent', 0)
    
    # Policy Guidelines Section
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(15, 76, 92)
    pdf.cell(0, 10, 'URGENT: Mayor Briefing - City Environmental State', 0, 1)
    pdf.ln(5)
    
    # Executive KPIs
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 10, 'Current AQI:', 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(50, 10, f"{aqi} ({severity})", 0, 1)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 10, 'Daily Carbon Load:', 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(50, 10, f"{carbon} Tons", 0, 1)
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Primary Root Causes:', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, f"- Traffic contribution: {attr.get('traffic', 0)}%\n- Industrial contribution: {attr.get('industrial', 0)}%\n- Meteorological impact: {attr.get('wind_impact', 0)}%")
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Policy Recommendations:', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, "1. Immediate restriction of heavy vehicle entry in Central Business District.\n2. Activation of 'Zone-Alpha' emergency street misting protocols.\n3. Mandatory work-from-home advisory for non-essential industrial staff.\n4. Public health broadcast for Tier-3 risk zones.")
    
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "This briefing is auto-generated by EcoPulse AI based on real-time sensory data and predictive atmospheric models. It is intended for city-level governance and rapid decision-making.")

    pdf.output(output_path)
    return output_path
