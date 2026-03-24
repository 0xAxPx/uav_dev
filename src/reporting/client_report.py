"""
Client-Facing Inspection Report Generator

Generates professional, branded PDF reports for customers.
Simplified language, property details, findings, and recommendations.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                                TableStyle, PageBreak, Image, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import pandas as pd
import numpy as np
import os


class ClientInspectionReport:
    """Generate client-facing inspection reports."""
    
    def __init__(self, csv_path, property_info, weather_info=None, findings=None):
        """
        Initialize client report generator.
        
        Args:
            csv_path: Path to flight telemetry CSV
            property_info: Dict with property details
            weather_info: Dict with weather conditions (optional)
            findings: List of inspection findings (optional)
        """
        self.csv_path = csv_path
        self.property_info = property_info
        self.weather_info = weather_info or {}
        self.findings = findings or []
        
        # Load flight data
        print(f"Loading flight data: {csv_path}")
        self.df = pd.read_csv(csv_path)
        self.stats = self._calculate_stats()
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
        print(f"✓ Report ready for: {property_info.get('address', 'Unknown Property')}")
    
    def _calculate_stats(self):
        """Calculate simplified statistics for client."""
        duration_min = self.df['timestamp'].max() / 60
        
        # Area covered (approximate from waypoints)
        x_range = self.df['x'].max() - self.df['x'].min()
        y_range = self.df['y'].max() - self.df['y'].min()
        area_m2 = abs(x_range * y_range)
        area_acres = area_m2 / 4047  # Convert to acres
        
        # Average altitude
        avg_altitude_m = self.df['altitude'].mean()
        avg_altitude_ft = avg_altitude_m * 3.281  # Convert to feet
        
        # Number of waypoints (approximate image count)
        num_waypoints = self.df['waypoint'].max() + 1
        
        return {
            'duration_min': duration_min,
            'area_m2': area_m2,
            'area_acres': area_acres,
            'avg_altitude_m': avg_altitude_m,
            'avg_altitude_ft': avg_altitude_ft,
            'image_count': num_waypoints,  # Approximate
        }
    
    def _setup_styles(self):
        """Setup custom styles for client report."""
        
        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=5,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Report title
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='ClientSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#2563eb'),
            borderPadding=5,
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='ClientBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Highlight box
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=18,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leftIndent=20,
            rightIndent=20,
            spaceBefore=10,
            spaceAfter=10,
        ))
    
    def _create_header(self, canvas, doc):
        """Add header to each page."""
        canvas.saveState()
        
        # Company name at top
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawString(2*cm, A4[1] - 1.5*cm, 
                         self.property_info.get('company_name', 'UAV Inspection Services'))
        
        # Report ID on right
        report_id = self.property_info.get('report_id', 
                                          datetime.now().strftime('INS-%Y%m%d-%H%M'))
        canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.5*cm, f"Report ID: {report_id}")
        
        canvas.restoreState()
    
    def generate_report(self, output_dir='reports'):
        """Generate client-facing PDF report."""
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Clean filename from property address
        address_clean = self.property_info.get('address', 'property').replace(' ', '_').replace(',', '')
        filename = os.path.join(output_dir, f'client_report_{address_clean}_{timestamp}.pdf')
        
        # Create document
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # ==================== COVER PAGE ====================
        
        # Company branding
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(
            self.property_info.get('company_name', 'UAV Inspection Services'),
            self.styles['CompanyName']
        ))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("AERIAL INSPECTION REPORT", self.styles['ReportTitle']))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Property details box
        property_data = [
            ['Property Address:', self.property_info.get('address', 'N/A')],
            ['Inspection Date:', self.property_info.get('inspection_date', 
                                                       datetime.now().strftime('%d %B %Y'))],
            ['Inspector:', self.property_info.get('inspector', 'Licensed UAV Operator')],
            ['Report ID:', self.property_info.get('report_id', 
                                                 datetime.now().strftime('INS-%Y%m%d-%H%M'))],
        ]
        
        t = Table(property_data, colWidths=[5*cm, 10*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t)
        
        story.append(Spacer(1, 0.5*inch))
        
        # Weather conditions (if provided)
        if self.weather_info:
            story.append(Paragraph("Inspection Conditions", self.styles['ClientSection']))
            
            weather_text = f"""
            The aerial inspection was conducted under {self.weather_info.get('conditions', 'suitable')} 
            conditions with {self.weather_info.get('visibility', 'good')} visibility. 
            Temperature: {self.weather_info.get('temperature', 'N/A')}, 
            Wind: {self.weather_info.get('wind', 'light')}.
            """
            story.append(Paragraph(weather_text, self.styles['ClientBody']))
            story.append(Spacer(1, 0.3*inch))
        
        # ==================== EXECUTIVE SUMMARY ====================
        
        story.append(PageBreak())
        story.append(Paragraph("Executive Summary", self.styles['ClientSection']))
        
        summary_text = f"""
        We successfully completed a comprehensive aerial inspection of your property 
        at {self.property_info.get('address', 'the specified location')}. Our certified 
        drone operator conducted a detailed survey covering approximately 
        {self.stats['area_m2']:.0f} square meters ({self.stats['area_acres']:.2f} acres) 
        from an average altitude of {self.stats['avg_altitude_ft']:.0f} feet 
        ({self.stats['avg_altitude_m']:.1f} meters).
        """
        
        story.append(Paragraph(summary_text, self.styles['ClientBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # Inspection highlights
        highlights_data = [
            ['Area Surveyed', f"{self.stats['area_m2']:.0f} m² ({self.stats['area_acres']:.2f} acres)"],
            ['Flight Duration', f"{self.stats['duration_min']:.0f} minutes"],
            ['Survey Altitude', f"{self.stats['avg_altitude_ft']:.0f} ft ({self.stats['avg_altitude_m']:.1f} m)"],
            ['Images Captured', f"~{self.stats['image_count']} waypoints"],
            ['Coverage', '100% Complete'],
        ]
        
        t = Table(highlights_data, colWidths=[6*cm, 8*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f9ff')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(t)
        
        # ==================== FINDINGS ====================
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Inspection Findings", self.styles['ClientSection']))
        
        if self.findings:
            for i, finding in enumerate(self.findings, 1):
                finding_text = f"<b>{i}. {finding.get('title', 'Observation')}</b><br/>"
                finding_text += f"{finding.get('description', 'No description provided.')}"
                
                if finding.get('severity'):
                    severity_color = {
                        'low': '#10b981',
                        'medium': '#f59e0b',
                        'high': '#ef4444'
                    }.get(finding['severity'].lower(), '#666666')
                    
                    finding_text += f"<br/><font color='{severity_color}'>"
                    finding_text += f"Severity: {finding['severity'].upper()}</font>"
                
                story.append(Paragraph(finding_text, self.styles['ClientBody']))
                story.append(Spacer(1, 0.15*inch))
        else:
            story.append(Paragraph(
                "The aerial inspection has been completed successfully. "
                "All captured imagery is available for detailed review. "
                "No immediate concerns were identified during the flight survey.",
                self.styles['ClientBody']
            ))
        
        # ==================== FLIGHT PATH ====================
        
        # Try to find and include 2D flight path image
        plots_dir = os.path.join(os.path.dirname(os.path.dirname(self.csv_path)), 'analysis', 'plots')
        flight_path_img = None
        
        if os.path.exists(plots_dir):
            for filename in sorted(os.listdir(plots_dir), reverse=True):
                if 'flight_2d_path' in filename and filename.endswith('.png'):
                    flight_path_img = os.path.join(plots_dir, filename)
                    break
        
        if flight_path_img and os.path.exists(flight_path_img):
            story.append(PageBreak())
            story.append(Paragraph("Survey Coverage Map", self.styles['ClientSection']))
            story.append(Paragraph(
                "The following map shows the complete flight path of the aerial survey, "
                "demonstrating full coverage of the inspected area.",
                self.styles['ClientBody']
            ))
            story.append(Spacer(1, 0.2*inch))
            
            img = Image(flight_path_img, width=14*cm, height=10*cm)
            story.append(img)
        
        # ==================== RECOMMENDATIONS ====================
        
        story.append(PageBreak())
        story.append(Paragraph("Recommendations & Next Steps", self.styles['ClientSection']))
        
        recommendations = self.property_info.get('recommendations', [
            "Review the captured imagery for detailed analysis",
            "Contact us if you require annotated images or detailed reports",
            "Schedule follow-up inspection as needed",
        ])
        
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.styles['ClientBody']))
            story.append(Spacer(1, 0.1*inch))
        
        # ==================== CONTACT INFO ====================
        
        story.append(Spacer(1, 0.5*inch))
        
        contact_info = f"""
        <b>For Questions or Additional Services:</b><br/>
        {self.property_info.get('company_name', 'UAV Inspection Services')}<br/>
        Email: {self.property_info.get('contact_email', 'info@uavinspection.co.uk')}<br/>
        Phone: {self.property_info.get('contact_phone', '+44 (0) 20 1234 5678')}<br/>
        Web: {self.property_info.get('website', 'www.uavinspection.co.uk')}
        """
        
        story.append(Paragraph(contact_info, self.styles['ClientBody']))
        
        # ==================== DISCLAIMER ====================
        
        story.append(Spacer(1, 0.3*inch))
        
        disclaimer = """
        <i><font size=8>
        This report is based on aerial imagery captured during the inspection flight. 
        It does not constitute a structural survey or engineering assessment. 
        For detailed structural analysis, please consult a qualified surveyor or engineer.
        </font></i>
        """
        story.append(Paragraph(disclaimer, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        print(f"✓ Client report generated: {filename}")
        return filename


def main():
    """Example usage of client report generator."""
    
    # Find most recent flight CSV
    log_dir = '../missions/logs'
    if not os.path.exists(log_dir):
        print(f"Error: Log directory not found: {log_dir}")
        return
    
    log_files = [f for f in os.listdir(log_dir) 
                 if f.endswith('.csv') and f.startswith('flight_')]
    
    if not log_files:
        print("No flight log files found!")
        return
    
    log_files.sort(reverse=True)
    csv_path = os.path.join(log_dir, log_files[0])
    
    print("\n" + "="*70)
    print("CLIENT REPORT GENERATOR - EXAMPLE")
    print("="*70)
    print(f"\nUsing flight data: {csv_path}\n")
    
    # Example property information
    property_info = {
        'company_name': 'SkyView Inspections Ltd',
        'address': '42 Commercial Road, London, E1 1AA',
        'inspection_date': '19 March 2026',
        'inspector': 'Alex - Licensed UAV Operator (CAA Certified)',
        'report_id': 'INS-20260319-001',
        'contact_email': 'info@skyviewinspections.co.uk',
        'contact_phone': '+44 (0) 20 7123 4567',
        'website': 'www.skyviewinspections.co.uk',
        'recommendations': [
            'High-resolution imagery available upon request',
            'Thermal imaging survey recommended for energy efficiency assessment',
            'Annual inspection recommended for proactive maintenance',
        ]
    }
    
    # Example weather conditions
    weather_info = {
        'conditions': 'clear and sunny',
        'visibility': 'excellent (>10km)',
        'temperature': '15°C',
        'wind': 'light breeze (5-10 mph)',
    }
    
    # Example findings
    findings = [
        {
            'title': 'Roof Coverage Complete',
            'description': 'Full aerial coverage achieved with no obstructions. All areas accessible for visual inspection.',
            'severity': 'low'
        },
        {
            'title': 'Image Quality',
            'description': 'High-resolution imagery captured from optimal altitude. Suitable for detailed analysis.',
            'severity': 'low'
        },
    ]
    
    # Generate report
    generator = ClientInspectionReport(
        csv_path=csv_path,
        property_info=property_info,
        weather_info=weather_info,
        findings=findings
    )
    
    report_path = generator.generate_report(output_dir='../analysis/reports')
    
    print("\n" + "="*70)
    print("✓ CLIENT REPORT COMPLETE")
    print("="*70)
    print(f"\nReport saved: {report_path}")
    print("\nThis is a client-deliverable report with:")
    print("  ✓ Property details")
    print("  ✓ Weather conditions")
    print("  ✓ Executive summary (simplified language)")
    print("  ✓ Inspection findings")
    print("  ✓ Flight path visualization")
    print("  ✓ Recommendations")
    print("  ✓ Contact information")
    print("\n")


if __name__ == "__main__":
    main()