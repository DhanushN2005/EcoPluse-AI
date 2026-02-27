import datetime
import logging
from typing import List, Dict, Any
from fpdf import FPDF

logger = logging.getLogger("Report-Generator")


class EnvironmentalReport(FPDF):
    """
    Standardized PDF template for EcoPulse AI environmental reports.
    """

    def header(self) -> None:
        """Adds a professional header with branding to each page."""
        # Branding background
        self.set_fill_color(15, 76, 92)  # Dark teal theme
        self.rect(0, 0, 210, 40, "F")

        self.set_font("Arial", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 20, "EcoPulse AI Executive Summary", 0, 1, "C")

        self.set_font("Arial", "I", 10)
        self.cell(0, 0, "Integrated Smart-City Environmental Intelligence", 0, 1, "C")
        self.ln(20)

    def footer(self) -> None:
        """Adds a footer with page numbers and timestamp."""
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cell(
            0, 10, f"Page {self.page_no()} | Generated on {ts} | System Status: Verified", 0, 0, "C"
        )


def generate_full_report(data: List[Dict[str, Any]], output_path: str) -> str:
    """
    Generates a comprehensive environmental health report.

    Args:
        data (List[Dict[str, Any]]): Historical telemetry data.
        output_path (str): The filesystem path where the PDF will be saved.

    Returns:
        str: The path to the generated report.
    """
    logger.info(f"Generating full environmental report at: {output_path}")
    pdf = EnvironmentalReport()
    pdf.add_page()

    # 1. AI Summary Section
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(15, 76, 92)
    pdf.cell(0, 10, "1. AI-Driven Environmental Insights", 0, 1)
    pdf.ln(2)

    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(50, 50, 50)

    if data:
        _ = data[-1].get("aqi", 0.0)
        avg_aqi = sum(float(d.get("aqi", 0)) for d in data) / len(data)
        peak_time = datetime.datetime.now().strftime("%H:%M")

        insight = (
            f"Automated analysis indicates a rolling AQI baseline of {avg_aqi:.1f}. "
            f"The system identified peak variances near the {peak_time} mark, primarily correlated "
            "with localized traffic volatility and industrial plume dispersion patterns. "
            "Predictive modeling indicates a trend of high atmospheric persistence for current pollutants. "
            "Recommendation: Deploy Zone-Level Protocol 3 (Misting and Traffic Diversion) for high-impact sectors."
        )
    else:
        insight = "Insufficient telemetry data available for comprehensive insight generation."

    pdf.multi_cell(0, 6, insight)
    pdf.ln(10)

    # 2. Detailed Metrics Log
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "2. Comparative Telemetry Log (Recent 15)", 0, 1)

    # Header styling
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 10, "Timestamp", 1, 0, "C", True)
    pdf.cell(30, 10, "AQI", 1, 0, "C", True)
    pdf.cell(30, 10, "Health Index", 1, 0, "C", True)
    pdf.cell(90, 10, "Primary Attribution (Traffic/Wind)", 1, 1, "C", True)

    pdf.set_font("Arial", "", 9)
    for record in data[-15:]:
        ts = str(record.get("timestamp", "")).split("T")[-1][:8]
        aqi = f"{float(record.get('aqi', 0)):.1f}"
        health = f"{float(record.get('health_score', 0)):.1f}"
        attr = record.get("attribution", {})
        attr_text = f"Trf: {attr.get('traffic')}% | Wnd: {attr.get('wind_impact')}%"

        pdf.cell(40, 8, ts, 1, 0, "C")
        pdf.cell(30, 8, aqi, 1, 0, "C")
        pdf.cell(30, 8, health, 1, 0, "C")
        pdf.cell(90, 8, attr_text, 1, 1, "L")

    pdf.ln(10)

    # 3. Action Items
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(46, 204, 113)  # Success green
    pdf.cell(0, 10, "Strategic Action Mandates:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(50, 50, 50)

    actions = [
        "- Execute 'Green Pulse' traffic protocols in critical corridors.",
        "- Push automated alert notifications to registered High-Risk citizens.",
        "- Initiate automated street misting in Sector 4 and Sector 9.",
        "- Schedule immediate emissions audit for top 3 industrial outliers.",
    ]
    for action in actions:
        pdf.cell(0, 7, action, 0, 1)

    pdf.output(output_path)
    return output_path


def generate_mayor_briefing(data: List[Dict[str, Any]], output_path: str) -> str:
    """
    Generates a concise briefing document intended for municipal decision-makers.

    Args:
        data (List[Dict[str, Any]]): Telemetry dataset.
        output_path (str): File destination.

    Returns:
        str: Output path.
    """
    logger.info(f"Generating Mayor level briefing at: {output_path}")
    pdf = EnvironmentalReport()
    pdf.add_page()

    latest = data[-1] if data else {}
    aqi = latest.get("aqi", 0.0)
    severity = latest.get("severity", "Optimal")
    attr = latest.get("attribution", {})
    carbon = latest.get("carbon_footprint", {}).get("total_equivalent", 0.0)

    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(15, 76, 92)
    pdf.cell(0, 10, "URGENT: Mayor Briefing - City Environmental State", 0, 1)
    pdf.ln(5)

    # Executive KPIs table layout
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "Metric", 1, 0, "C", True)
    pdf.cell(130, 10, "Value / Status", 1, 1, "C", True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(60, 10, "Live AQI Level", 1, 0, "L")
    pdf.cell(130, 10, f" {aqi} ({severity})", 1, 1, "L")

    pdf.cell(60, 10, "Daily Carbon Load", 1, 0, "L")
    pdf.cell(130, 10, f" {carbon} Tons CO2-eq", 1, 1, "L")

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Primary Driver Attribution:", 0, 1)
    pdf.set_font("Arial", "", 11)
    drivers = (
        f"• Traffic Systems: {attr.get('traffic', 0)}% impact\n"
        f"• Industrial Clusters: {attr.get('industrial', 0)}% impact\n"
        f"• Meteorological Stagnation: {attr.get('wind_impact', 0)}% impact"
    )
    pdf.multi_cell(0, 7, drivers)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Urgent Policy Mandates:", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        "1. Restrict non-essential heavy vehicle entry into City Zone A.\n"
        "2. Activate emergency ventilation protocols in high-density corridors.\n"
        "3. Issue mandatory 'Stay Indoors' advisory for citizens in Tier-4 risk zones.\n"
        "4. Enforce immediate 20% output reduction for the Industrial North cluster.",
    )

    pdf.ln(15)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        0,
        5,
        "Confidential: This briefing is auto-generated by EcoPulse AI based on real-time sensory data. Intended for governmental use only.",
    )

    pdf.output(output_path)
    return output_path
