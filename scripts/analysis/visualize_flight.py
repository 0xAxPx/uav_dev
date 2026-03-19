"""
Flight Data Visualization
Reads telemetry CSV and creates 4 plots:
1. 2D Flight Path (top view)
2. Altitude Profile (over time)
3. Speed Profile (over time)
4. 3D Flight Path
"""

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import sys
import os
from datetime import datetime


def load_flight_data(csv_path):
    """Load flight telemetry from CSV."""
    print(f"Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} telemetry readings")
    print(f"Flight duration: {df['timestamp'].max():.1f} seconds")
    print(f"Waypoints: {df['waypoint'].min()} to {df['waypoint'].max()}")
    return df


def plot_2d_path(df, save_path):
    """Plot 2D flight path (top view)."""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Color by waypoint number for clear visualization
    scatter = ax.scatter(df['y'], df['x'], c=df['waypoint'], 
                        cmap='viridis', s=10, alpha=0.6)
    
    # Plot flight path line
    ax.plot(df['y'], df['x'], 'gray', linewidth=0.5, alpha=0.3)
    
    # Mark start and end
    ax.plot(df['y'].iloc[0], df['x'].iloc[0], 'go', markersize=15, 
            label='Start', zorder=5)
    ax.plot(df['y'].iloc[-1], df['x'].iloc[-1], 'ro', markersize=15, 
            label='End', zorder=5)
    
    # Labels and formatting
    ax.set_xlabel('East (m)', fontsize=12)
    ax.set_ylabel('North (m)', fontsize=12)
    ax.set_title('2D Flight Path - Grid Mission', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Waypoint Number', fontsize=10)
    
    # Legend
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


def plot_altitude_profile(df, save_path):
    """Plot altitude over time."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Altitude line
    ax.plot(df['timestamp'], df['altitude'], 'b-', linewidth=1.5, label='Actual Altitude')
    
    # Target altitude (if mostly at 15m during grid)
    grid_start = df[df['waypoint'] == 1]['timestamp'].min() if 1 in df['waypoint'].values else 0
    grid_end = df[df['waypoint'] == df['waypoint'].max() - 1]['timestamp'].max()
    ax.axhline(y=15, color='r', linestyle='--', linewidth=2, 
               label='Target Grid Altitude (15m)', alpha=0.7)
    
    # Tolerance band
    ax.fill_between(df['timestamp'], 14.5, 15.5, color='red', alpha=0.1, 
                    label='±0.5m Tolerance')
    
    # Labels
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('Altitude (m)', fontsize=12)
    ax.set_title('Altitude Profile Over Time', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


def plot_speed_profile(df, save_path):
    """Plot speed over time."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Ground speed
    ax.plot(df['timestamp'], df['ground_speed'], 'b-', linewidth=1, 
            label='Ground Speed', alpha=0.8)
    
    # Vertical speed (absolute value for visualization)
    ax.plot(df['timestamp'], df['vertical_speed'].abs(), 'r-', linewidth=1, 
            label='Vertical Speed (abs)', alpha=0.8)
    
    # Labels
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('Speed (m/s)', fontsize=12)
    ax.set_title('Speed Profile Over Time', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


def plot_3d_path(df, save_path):
    """Plot 3D flight path."""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Color by time progression
    scatter = ax.scatter(df['y'], df['x'], df['altitude'], 
                        c=df['timestamp'], cmap='plasma', 
                        s=10, alpha=0.6)
    
    # Flight path line
    ax.plot(df['y'], df['x'], df['altitude'], 'gray', 
            linewidth=0.5, alpha=0.3)
    
    # Start and end markers
    ax.scatter(df['y'].iloc[0], df['x'].iloc[0], df['altitude'].iloc[0], 
              color='green', s=200, marker='o', label='Start', 
              edgecolors='black', linewidths=2)
    ax.scatter(df['y'].iloc[-1], df['x'].iloc[-1], df['altitude'].iloc[-1], 
              color='red', s=200, marker='o', label='End', 
              edgecolors='black', linewidths=2)
    
    # Labels
    ax.set_xlabel('East (m)', fontsize=11)
    ax.set_ylabel('North (m)', fontsize=11)
    ax.set_zlabel('Altitude (m)', fontsize=11)
    ax.set_title('3D Flight Path - Complete Mission', fontsize=14, fontweight='bold')
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, pad=0.1, shrink=0.8)
    cbar.set_label('Time (seconds)', fontsize=10)
    
    # Legend
    ax.legend(loc='upper left')
    
    # Better viewing angle
    ax.view_init(elev=25, azim=45)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


def generate_summary_stats(df):
    """Print flight statistics."""
    print("\n" + "="*60)
    print("FLIGHT STATISTICS")
    print("="*60)
    
    duration = df['timestamp'].max()
    print(f"Total Duration: {duration:.1f}s ({duration/60:.1f} minutes)")
    print(f"Total Waypoints: {df['waypoint'].max() + 1}")
    print(f"Telemetry Readings: {len(df)}")
    
    # Distance calculation
    dx = df['x'].diff()
    dy = df['y'].diff()
    distance = np.sqrt(dx**2 + dy**2).sum()
    print(f"Total Distance (horizontal): {distance:.1f}m")
    
    # Altitude stats
    print(f"\nAltitude Statistics:")
    print(f"  Max: {df['altitude'].max():.2f}m")
    print(f"  Mean: {df['altitude'].mean():.2f}m")
    print(f"  Min: {df['altitude'].min():.2f}m")
    
    # Speed stats
    print(f"\nSpeed Statistics:")
    print(f"  Max Ground Speed: {df['ground_speed'].max():.2f} m/s")
    print(f"  Avg Ground Speed: {df['ground_speed'].mean():.2f} m/s")
    print(f"  Max Vertical Speed: {df['vertical_speed'].abs().max():.2f} m/s")
    
    # Battery
    battery_start = df['battery'].iloc[0]
    battery_end = df['battery'].iloc[-1]
    if battery_start > 0 and battery_end > 0:
        print(f"\nBattery:")
        print(f"  Start: {battery_start}%")
        print(f"  End: {battery_end}%")
        print(f"  Used: {battery_start - battery_end}%")
    
    print("="*60 + "\n")


def visualize_flight(csv_path, output_dir='plots'):
    """Main function to generate all visualizations."""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    df = load_flight_data(csv_path)
    
    # Generate stats
    generate_summary_stats(df)
    
    # Create timestamp for plot filenames
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Generate all plots
    print("\nGenerating visualizations...")
    
    plot_2d_path(df, os.path.join(output_dir, f'flight_2d_path_{timestamp}.png'))
    plot_altitude_profile(df, os.path.join(output_dir, f'flight_altitude_{timestamp}.png'))
    plot_speed_profile(df, os.path.join(output_dir, f'flight_speed_{timestamp}.png'))
    plot_3d_path(df, os.path.join(output_dir, f'flight_3d_path_{timestamp}.png'))
    
    print(f"\n✓ All visualizations saved to: {output_dir}/")
    print(f"✓ Analysis complete!\n")
    return output_dir


if __name__ == "__main__":
    # Check if CSV path provided
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        # Use most recent log file
        log_dir = '../missions/logs'
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.csv') and f.startswith('flight_')]
            if log_files:
                log_files.sort(reverse=True)  # Most recent first
                csv_path = os.path.join(log_dir, log_files[0])
                print(f"Using most recent log: {csv_path}")
            else:
                print("No CSV files found in logs/")
                sys.exit(1)
        else:
            print("Please provide CSV path: python visualize_flight.py <path_to_csv>")
            sys.exit(1)
    
    visualize_flight(csv_path)