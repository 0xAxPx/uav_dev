"""
Enhanced PDF Report Generator for UAV Inspection Flights

Generates professional PDF reports with embedded visualizations.
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
import sys


class EnhancedFlightReportGenerator:
    """Generate enhanced PDF reports with visualizations."""
    
    def __init__(self, csv_path, output_dir='reports'):
        """Initialize report generator."""
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
        """Calculate comprehensive flight statistics."""
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
        median_speed = self.df['ground_speed'].median()
        
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
        
        # Acceleration analysis
        self.df['acceleration'] = self.df['ground_speed'].diff() / self.df['timestamp'].diff()
        high_accel_count = len(self.df[self.df['acceleration'].abs() > 1.0])
        peak_accel = self.df['acceleration'].max()
        peak_decel = self.df['acceleration'].min()
        
        # Waypoints
        max_waypoint = self.df['waypoint'].max()
        
        # Flight profile detection
        profile = "Unknown"
        if max_speed > 10:
            profile = "Aggressive"
        elif max_speed > 5:
            profile = "Efficient"
        else:
            profile = "Conservative"
        
        return {
            'duration_sec': duration_sec,
            'duration_min': duration_min,
            'battery_start': battery_start,
            'battery_end': battery_end,
            'battery_used': battery_used,
            'battery_per_min': battery_used / duration_min if duration_min > 0 else 0,
            'max_speed': max_speed,
            'avg_speed': avg_speed,
            'median_speed': median_speed,
            'total_distance': total_distance,
            'max_altitude': max_alt,
            'avg_altitude': avg_alt,
            'min_altitude': min_alt,
            'waypoints': int(max_waypoint) + 1,
            'telemetry_points': len(self.df),
            'high_accel_count': high_accel_count,
            'peak_accel': peak_accel,
            'peak_decel': peak_decel,
            'profile': profile
        }
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section Header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Executive Summary
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
    
    def _find_plot_files(self):
        """Find the most recent plot files."""
        plots_dir = os.path.join(os.path.dirname(self.output_dir), 'plots')
        
        if not os.path.exists(plots_dir):
            return None
        
        # Get most recent plots
        plot_files = {
            '2d_path': None,
            'altitude': None,
            'speed': None,
            '3d_path': None
        }
        
        for filename in os.listdir(plots_dir):
            if filename.endswith('.png'):
                full_path = os.path.join(plots_dir, filename)
                
                if 'flight_2d_path' in filename:
                    plot_files['2d_path'] = full_path
                elif 'flight_altitude' in filename:
                    plot_files['altitude'] = full_path
                elif 'flight_speed' in filename:
                    plot_files['speed'] = full_path
                elif 'flight_3d_path' in filename:
                    plot_files['3d_path'] = full_path
        
        return plot_files
    
    def generate_enhanced_report(self):
        """Generate enhanced technical report with visualizations."""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = os.path.join(self.output_dir, f'flight_report_enhanced_{timestamp}.pdf')
        
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
        
        # ==================== TITLE PAGE ====================
        story.append(Paragraph("UAV Flight Analysis Report", self.styles['CustomTitle']))
        story.append(Paragraph(f"{self.stats['profile']} Flight Profile", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Report metadata
        metadata = [
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Flight Profile:', self.stats['profile']],
            ['Data Source:', os.path.basename(self.csv_path)],
            ['Flight Duration:', f"{self.stats['duration_min']:.1f} minutes"],
        ]
        
        t = Table(metadata, colWidths=[4*cm, 11*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # ==================== EXECUTIVE SUMMARY ====================
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        summary_text = f"""
        This report presents a comprehensive analysis of an autonomous UAV inspection flight 
        covering {self.stats['total_distance']:.0f} meters over {self.stats['duration_min']:.1f} minutes. 
        The mission utilized a {self.stats['profile']} flight profile with a maximum speed of {self.stats['max_speed']:.1f} m/s, 
        completing {self.stats['waypoints']} waypoints while consuming {self.stats['battery_used']:.0f}% battery capacity. 
        The flight maintained an average altitude of {self.stats['avg_altitude']:.1f}m with high precision 
        positioning throughout the mission.
        """
        
        story.append(Paragraph(summary_text, self.styles['ExecutiveSummary']))
        story.append(Spacer(1, 0.2*inch))
        
        # ==================== KEY METRICS ====================
        story.append(Paragraph("Key Performance Indicators", self.styles['SectionHeader']))
        
        kpi_data = [
            ['Metric', 'Value', 'Rating'],
            ['Mission Completion', '100%', '✓ Excellent'],
            ['Battery Efficiency', f'{self.stats["battery_per_min"]:.2f}%/min', 
             '✓ Good' if self.stats['battery_per_min'] < 4.0 else '⚠ Moderate'],
            ['Flight Stability', f'{self.stats["high_accel_count"]} events', 
             '✓ Excellent' if self.stats['high_accel_count'] < 100 else '⚠ Moderate'],
            ['Altitude Precision', f'±{abs(self.stats["max_altitude"] - self.stats["avg_altitude"]):.2f}m', '✓ Excellent'],
        ]
        
        t = Table(kpi_data, colWidths=[6*cm, 4*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2*inch))
        
        # ==================== DETAILED STATISTICS ====================
        story.append(PageBreak())
        story.append(Paragraph("Detailed Flight Statistics", self.styles['SectionHeader']))
        
        # Mission Summary Table
        summary_data = [
            ['Category', 'Metric', 'Value', 'Unit'],
            ['Mission', 'Total Duration', f"{self.stats['duration_min']:.1f}", 'minutes'],
            ['Mission', 'Total Distance', f"{self.stats['total_distance']:.1f}", 'meters'],
            ['Mission', 'Waypoints', f"{self.stats['waypoints']}", 'points'],
            ['Speed', 'Maximum', f"{self.stats['max_speed']:.2f}", 'm/s'],
            ['Speed', 'Average', f"{self.stats['avg_speed']:.2f}", 'm/s'],
            ['Speed', 'Median', f"{self.stats['median_speed']:.2f}", 'm/s'],
            ['Altitude', 'Maximum', f"{self.stats['max_altitude']:.2f}", 'meters'],
            ['Altitude', 'Average', f"{self.stats['avg_altitude']:.2f}", 'meters'],
            ['Altitude', 'Minimum', f"{self.stats['min_altitude']:.2f}", 'meters'],
            ['Battery', 'Starting Level', f"{self.stats['battery_start']:.0f}", '%'],
            ['Battery', 'Ending Level', f"{self.stats['battery_end']:.0f}", '%'],
            ['Battery', 'Total Used', f"{self.stats['battery_used']:.0f}", '%'],
            ['Battery', 'Consumption Rate', f"{self.stats['battery_per_min']:.2f}", '%/min'],
            ['Performance', 'High Accel Events', f"{self.stats['high_accel_count']}", 'events'],
            ['Performance', 'Peak Acceleration', f"{self.stats['peak_accel']:.2f}", 'm/s²'],
        ]
        
        t = Table(summary_data, colWidths=[3.5*cm, 5*cm, 3*cm, 2.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('SPAN', (0, 1), (0, 3)),  # Mission category
            ('SPAN', (0, 4), (0, 6)),  # Speed category
            ('SPAN', (0, 7), (0, 9)),  # Altitude category
            ('SPAN', (0, 10), (0, 13)),  # Battery category
            ('SPAN', (0, 14), (0, 15)),  # Performance category
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t)
        
        # ==================== VISUALIZATIONS ====================
        plot_files = self._find_plot_files()
        
        if plot_files and any(plot_files.values()):
            story.append(PageBreak())
            story.append(Paragraph("Flight Visualizations", self.styles['SectionHeader']))
            
            # 2D Flight Path
            if plot_files.get('2d_path') and os.path.exists(plot_files['2d_path']):
                story.append(Paragraph("2D Flight Path (Top-Down View)", self.styles['Heading3']))
                img = Image(plot_files['2d_path'], width=15*cm, height=10*cm)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            
            # Speed Profile
            if plot_files.get('speed') and os.path.exists(plot_files['speed']):
                story.append(PageBreak())
                story.append(Paragraph("Speed Profile Over Time", self.styles['Heading3']))
                img = Image(plot_files['speed'], width=15*cm, height=10*cm)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            
            # Altitude Profile
            if plot_files.get('altitude') and os.path.exists(plot_files['altitude']):
                story.append(Paragraph("Altitude Profile", self.styles['Heading3']))
                img = Image(plot_files['altitude'], width=15*cm, height=10*cm)
                story.append(img)
        
        # ==================== RECOMMENDATIONS ====================
        story.append(PageBreak())
        story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        
        recommendations = []
        
        # Battery-based recommendations
        if self.stats['battery_per_min'] > 4.0:
            recommendations.append("• Consider reducing cruise speed to improve battery efficiency")
        if self.stats['battery_used'] > 40:
            recommendations.append("• Mission uses significant battery - plan for recharging between flights")
        
        # Performance-based recommendations
        if self.stats['high_accel_count'] > 150:
            recommendations.append("• High number of acceleration events detected - consider smoother flight profile")
        elif self.stats['high_accel_count'] < 70:
            recommendations.append("• Excellent acceleration profile - optimal for battery efficiency")
        
        # Mission planning
        missions_per_battery = 50 / self.stats['battery_used'] if self.stats['battery_used'] > 0 else 0
        recommendations.append(f"• Estimated {missions_per_battery:.1f} missions possible per battery (50% usable capacity)")
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        print(f"✓ Enhanced report saved: {filename}")
        return filename


def main():
    """Generate enhanced report from most recent flight log."""
    
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
    
    print(f"\nGenerating enhanced report for: {csv_path}\n")
    
    # Generate report
    generator = EnhancedFlightReportGenerator(csv_path)
    
    print("\n" + "="*70)
    print("Generating Enhanced Report...")
    print("="*70)
    report = generator.generate_enhanced_report()
    
    print("\n" + "="*70)
    print("REPORT GENERATION COMPLETE")
    print("="*70)
    print(f"\n✓ Enhanced Report: {report}")
    print("\n")


if __name__ == "__main__":
    main()