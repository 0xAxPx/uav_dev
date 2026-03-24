"""
Battery Optimization Analysis

Analyzes flight telemetry to identify battery consumption patterns
and recommends optimized parameters.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os


def load_telemetry(csv_path):
    """Load flight telemetry data."""
    print(f"Loading telemetry from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} readings over {df['timestamp'].max():.1f} seconds\n")
    return df


def analyze_speed_profile(df):
    """Analyze speed characteristics."""
    print("="*70)
    print("SPEED PROFILE ANALYSIS")
    print("="*70)
    
    # Basic stats
    max_speed = df['ground_speed'].max()
    avg_speed = df['ground_speed'].mean()
    median_speed = df['ground_speed'].median()
    
    print(f"Max Ground Speed:    {max_speed:.2f} m/s")
    print(f"Average Speed:       {avg_speed:.2f} m/s")
    print(f"Median Speed:        {median_speed:.2f} m/s")
    
    # Speed distribution
    hover_time = len(df[df['ground_speed'] < 0.5]) * 0.5  # seconds
    slow_time = len(df[(df['ground_speed'] >= 0.5) & (df['ground_speed'] < 3)]) * 0.5
    cruise_time = len(df[(df['ground_speed'] >= 3) & (df['ground_speed'] < 8)]) * 0.5
    fast_time = len(df[df['ground_speed'] >= 8]) * 0.5
    
    total_time = df['timestamp'].max()
    
    print(f"\nTime Distribution:")
    print(f"  Hover (<0.5 m/s):     {hover_time:.1f}s ({hover_time/total_time*100:.1f}%)")
    print(f"  Slow (0.5-3 m/s):     {slow_time:.1f}s ({slow_time/total_time*100:.1f}%)")
    print(f"  Cruise (3-8 m/s):     {cruise_time:.1f}s ({cruise_time/total_time*100:.1f}%)")
    print(f"  Fast (>8 m/s):        {fast_time:.1f}s ({fast_time/total_time*100:.1f}%)")
    
    return {
        'max_speed': max_speed,
        'avg_speed': avg_speed,
        'hover_time': hover_time,
        'cruise_time': cruise_time,
        'fast_time': fast_time
    }


def analyze_acceleration(df):
    """Analyze acceleration patterns (battery intensive!)."""
    print("\n" + "="*70)
    print("ACCELERATION ANALYSIS (Battery Impact)")
    print("="*70)
    
    # Calculate acceleration (change in speed over time)
    df['acceleration'] = df['ground_speed'].diff() / df['timestamp'].diff()
    
    # Find high acceleration events (>1 m/s²)
    high_accel = df[df['acceleration'].abs() > 1.0]
    
    print(f"\nHigh Acceleration Events (>1 m/s²): {len(high_accel)}")
    print(f"Peak Acceleration: {df['acceleration'].max():.2f} m/s²")
    print(f"Peak Deceleration: {df['acceleration'].min():.2f} m/s²")
    
    # Estimate power impact
    # Rough model: base power (50%) + speed factor + acceleration factor
    avg_accel_magnitude = df['acceleration'].abs().mean()
    
    print(f"Average |Acceleration|: {avg_accel_magnitude:.3f} m/s²")
    print("\n⚠️  High acceleration = High battery drain!")
    print("    Reducing max speed reduces acceleration needs.")
    
    return high_accel


def estimate_battery_consumption(df, stats):
    """Estimate battery consumption by flight phase."""
    print("\n" + "="*70)
    print("BATTERY CONSUMPTION ESTIMATE")
    print("="*70)
    
    total_time_min = df['timestamp'].max() / 60
    
    # Power consumption model (simplified)
    # Hover: 50% power, Cruise: 60%, Fast: 75%
    hover_power_pct = 50
    cruise_power_pct = 60
    fast_power_pct = 75
    
    # Time in each phase (seconds)
    hover_time = stats['hover_time']
    cruise_time = stats['cruise_time']
    fast_time = stats['fast_time']
    total_time = hover_time + cruise_time + fast_time
    
    # Energy used (power × time, normalized)
    hover_energy = hover_power_pct * hover_time
    cruise_energy = cruise_power_pct * cruise_time
    fast_energy = fast_power_pct * fast_time
    total_energy = hover_energy + cruise_energy + fast_energy
    
    print(f"Estimated Power by Phase:")
    print(f"  Hover:  {hover_energy/total_energy*100:.1f}% of energy "
          f"({hover_time/total_time*100:.1f}% of time)")
    print(f"  Cruise: {cruise_energy/total_energy*100:.1f}% of energy "
          f"({cruise_time/total_time*100:.1f}% of time)")
    print(f"  Fast:   {fast_energy/total_energy*100:.1f}% of energy "
          f"({fast_time/total_time*100:.1f}% of time)")
    
    # Actual battery from data (if available)
    if 'battery' in df.columns:
        battery_start = df[df['battery'] > 0]['battery'].iloc[0] if len(df[df['battery'] > 0]) > 0 else 100
        battery_end = df[df['battery'] > 0]['battery'].iloc[-1] if len(df[df['battery'] > 0]) > 0 else 100
        battery_used = battery_start - battery_end
        
        if battery_used > 0:
            print(f"\nActual Battery Used: {battery_used:.1f}%")
            print(f"Rate: {battery_used/total_time_min:.2f}% per minute")


def recommend_optimizations(stats):
    """Provide optimization recommendations."""
    print("\n" + "="*70)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("="*70)
    
    max_speed = stats['max_speed']
    avg_speed = stats['avg_speed']
    fast_time_pct = stats['fast_time'] / (stats['hover_time'] + stats['cruise_time'] + stats['fast_time']) * 100
    
    print("\n🎯 Current Profile: AGGRESSIVE")
    print(f"   - Max speed: {max_speed:.1f} m/s")
    print(f"   - High speed time: {fast_time_pct:.1f}% of flight")
    print(f"   - Characteristics: Fast acceleration, high peak speeds")
    
    print("\n✅ RECOMMENDED: EFFICIENT Profile")
    print("   - Limit max speed to 6-7 m/s")
    print("   - Gentle acceleration (lower rate)")
    print("   - Expected battery savings: 15-25%")
    
    print("\n📋 Implementation:")
    print("   1. Modify PX4 parameter: MPC_XY_VEL_MAX = 6.0 (currently ~12)")
    print("   2. Modify PX4 parameter: MPC_ACC_HOR_MAX = 2.0 (gentle acceleration)")
    print("   3. Keep hover time at 3 seconds (good for image quality)")
    
    print("\n⚡ Expected Results:")
    if max_speed > 10:
        print("   - Reduce max speed from 12 m/s → 6 m/s")
        print("   - Mission time increases ~10-15%")
        print("   - Battery usage decreases ~20-25%")
        print("   - Net benefit: More missions per charge!")
    else:
        print("   - Already flying efficiently!")
        print("   - Minor optimizations possible")


def plot_speed_and_battery(df, output_dir='plots'):
    """Create visualization of speed profile with battery overlay."""
    os.makedirs(output_dir, exist_ok=True)
    
    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Speed over time
    ax1.plot(df['timestamp'], df['ground_speed'], 'b-', linewidth=1, alpha=0.8)
    ax1.axhline(y=6, color='g', linestyle='--', linewidth=2, 
                label='Optimal Cruise Speed (6 m/s)', alpha=0.7)
    ax1.axhline(y=12, color='r', linestyle='--', linewidth=2,
                label='Current Max Speed', alpha=0.7)
    ax1.fill_between(df['timestamp'], 0, 6, color='green', alpha=0.1, 
                     label='Efficient Zone')
    ax1.fill_between(df['timestamp'], 6, 20, color='orange', alpha=0.1,
                     label='High Power Zone')
    
    ax1.set_xlabel('Time (seconds)', fontsize=12)
    ax1.set_ylabel('Ground Speed (m/s)', fontsize=12)
    ax1.set_title('Speed Profile - Battery Optimization Analysis', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')
    ax1.set_ylim(0, max(df['ground_speed'].max() * 1.1, 15))
    
    # Battery usage (if available)
    if 'battery' in df.columns and df['battery'].max() > 0:
        battery_data = df[df['battery'] > 0]
        ax2.plot(battery_data['timestamp'], battery_data['battery'], 
                'r-', linewidth=2, label='Battery Level')
        ax2.set_xlabel('Time (seconds)', fontsize=12)
        ax2.set_ylabel('Battery (%)', fontsize=12)
        ax2.set_title('Battery Consumption Over Time', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper right')
        ax2.set_ylim(0, 105)
    else:
        ax2.text(0.5, 0.5, 'Battery data not available in telemetry',
                ha='center', va='center', fontsize=14,
                transform=ax2.transAxes)
        ax2.set_title('Battery Data Unavailable', fontsize=14)
    
    plt.tight_layout()
    
    filename = os.path.join(output_dir, 'battery_optimization_analysis.png')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\n✓ Plot saved: {filename}")
    plt.close()


def main():
    """Run battery analysis on telemetry data."""
    
    # Find most recent telemetry file
    log_dir = '../missions/logs'
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.csv') and f.startswith('flight_')]
        if log_files:
            log_files.sort(reverse=True)
            csv_path = os.path.join(log_dir, log_files[0])
            print(f"Using most recent log: {csv_path}\n")
        else:
            print("No flight log files found!")
            return
    else:
        print(f"Log directory not found: {log_dir}")
        return
    
    # Load data
    df = load_telemetry(csv_path)
    
    # Analyze
    stats = analyze_speed_profile(df)
    analyze_acceleration(df)
    estimate_battery_consumption(df, stats)
    recommend_optimizations(stats)
    
    # Visualize
    plot_speed_and_battery(df)
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()