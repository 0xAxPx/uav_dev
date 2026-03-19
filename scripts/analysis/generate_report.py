"""
PDF Report Generator for UAV Inspection Flights

Generates professional PDF reports from flight telemetry data.
Two report types:
1. Technical Analysis Report (internal)
2. Client Inspection Report (deliverable)
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                                TableStyle, PageBreak, Image, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import pandas as pd
import numpy as np
import os
import sys


class FlightReportGenerator:
    """Generate PDF reports from flight telemetry data."""
    
    def __init__(self, csv_path, output_dir='reports'):
        """
        Initialize report generator.
        
        Args:
            csv_path: Path to flight telemetry CSV
            output_dir: Directory to save reports
        """
        self.csv_path = csv_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Load data
        print(f"Loading telemetry: {csv_path}")
        self.df = pd.read_csv(csv_path)
        
        # Calculate statistics
        self.stats = self._calculate_statistics()
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        print(f"✓ Loaded {len(self.df)} telemetry readings")
    
    def _calculate_statistics(self):
        """Calculate flight statistics."""
        duration_sec = self.df['timestamp'].max()
        duration_min = duration_sec / 60
        
        # Battery
        battery_data = self.df[self.df['battery'] > 0]
        if len(battery_data) > 0:
            battery_start = battery_data['battery'].iloc[0]
            battery_end = battery_data['battery'].iloc[-1]
            battery_used = battery_start - battery_end
        else:
            battery_start = battery_end = battery_used = 0
        
        # Speed
        max_speed = self.df['ground_speed'].max()
        avg_speed = self.df['ground_speed'].mean()
        
        # Distance
        total_distance = 0
        for i in range(1, len(self.df)):
            dx = self.df['x'].iloc[i] - self.df['x'].iloc[i-1]
            dy = self.df['y'].iloc[i] - self.df['y'].iloc[i-1]
            total_distance += np.sqrt(dx**2 + dy**2)
        
        # Altitude
        max_alt = self.df['altitude'].max()
        avg_alt = self.df['altitude'].mean()
        min_alt = self.df['altitude'].min()
        
        # Waypoints
        max_waypoint = self.df['waypoint'].max()
        
        return {
            'duration_sec': duration_sec,
            'duration_min': duration_min,
            'battery_start': battery_start,
            'battery_end': battery_end,
            'battery_used': battery_used,
            'battery_per_min': battery_used / duration_min if duration_min > 0 else 0,
            'max_speed': max_speed,
            'avg_speed': avg_speed,
            'total_distance': total_distance,
            'max_altitude': max_alt,
            'avg_altitude': avg_alt,
            'min_altitude': min_alt,
            'waypoints': int(max_waypoint) + 1,
            'telemetry_points': len(self.df)
        }
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section Header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Metric Label
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica'
        ))
        
        # Metric Value
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            fontName='Helvetica-Bold'
        ))
    
    def generate_technical_report(self):
        """Generate technical analysis report."""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = os.path.join(self.output_dir, f'technical_report_{timestamp}.pdf')
        
        # Create document
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Title Page
        story.append(Paragraph("UAV Flight Analysis Report", self.styles['CustomTitle']))
        story.append(Paragraph("Technical Performance Assessment", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Report metadata
        metadata = [
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Data Source:', os.path.basename(self.csv_path)],
            ['Flight Duration:', f"{self.stats['duration_min']:.1f} minutes"],
            ['Telemetry Points:', f"{self.stats['telemetry_points']:,}"]
        ]
        
        t = Table(metadata, colWidths=[4*cm, 10*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*inch))
        
        # Mission Summary Section
        story.append(Paragraph("Mission Summary", self.styles['SectionHeader']))
        
        summary_data = [
            ['Metric', 'Value', 'Unit'],
            ['Total Duration', f"{self.stats['duration_min']:.1f}", 'minutes'],
            ['Total Distance', f"{self.stats['total_distance']:.1f}", 'meters'],
            ['Waypoints Completed', f"{self.stats['waypoints']}", 'waypoints'],
            ['Average Speed', f"{self.stats['avg_speed']:.2f}", 'm/s'],
            ['Maximum Speed', f"{self.stats['max_speed']:.2f}", 'm/s'],
        ]
        
        t = Table(summary_data, colWidths=[6*cm, 4*cm, 3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # Battery Performance Section
        story.append(Paragraph("Battery Performance", self.styles['SectionHeader']))
        
        battery_data = [
            ['Metric', 'Value', 'Unit'],
            ['Starting Battery', f"{self.stats['battery_start']:.1f}", '%'],
            ['Ending Battery', f"{self.stats['battery_end']:.1f}", '%'],
            ['Battery Consumed', f"{self.stats['battery_used']:.1f}", '%'],
            ['Consumption Rate', f"{self.stats['battery_per_min']:.2f}", '%/min'],
        ]
        
        # Estimate missions per battery
        missions_per_battery = 50 / self.stats['battery_used'] if self.stats['battery_used'] > 0 else 0
        battery_data.append(['Missions per Battery', f"{missions_per_battery:.1f}", 'missions'])
        
        t = Table(battery_data, colWidths=[6*cm, 4*cm, 3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # Altitude Performance
        story.append(Paragraph("Altitude Performance", self.styles['SectionHeader']))
        
        altitude_data = [
            ['Metric', 'Value', 'Unit'],
            ['Maximum Altitude', f"{self.stats['max_altitude']:.2f}", 'meters'],
            ['Average Altitude', f"{self.stats['avg_altitude']:.2f}", 'meters'],
            ['Minimum Altitude', f"{self.stats['min_altitude']:.2f}", 'meters'],
        ]
        
        t = Table(altitude_data, colWidths=[6*cm, 4*cm, 3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(t)
        
        # Build PDF
        doc.build(story)
        print(f"✓ Technical report saved: {filename}")
        return filename


def main():
    """Generate report from most recent flight log."""
    
    # Find most recent CSV
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
    
    print(f"\nGenerating report for: {csv_path}\n")
    
    # Generate reports
    generator = FlightReportGenerator(csv_path)
    
    print("\n" + "="*70)
    print("Generating Technical Report...")
    print("="*70)
    tech_report = generator.generate_technical_report()
    
    print("\n" + "="*70)
    print("REPORT GENERATION COMPLETE")
    print("="*70)
    print(f"\n✓ Technical Report: {tech_report}")
    print("\n")


if __name__ == "__main__":
    main()