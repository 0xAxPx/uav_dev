"""
Grid Configuration Test Suite

Tests multiple grid configurations and compares performance metrics.
Helps determine optimal settings for different inspection scenarios.
"""

from grid_mission import GridMission
import math
import csv
from datetime import datetime


def calculate_total_distance(waypoints):
    """
    Calculate total flight path distance.
    
    Args:
        waypoints: List of (x, y, z) tuples
        
    Returns:
        float: Total distance in meters
    """
    total = 0
    for i in range(len(waypoints) - 1):
        x1, y1, z1 = waypoints[i]
        x2, y2, z2 = waypoints[i + 1]
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
        total += distance
    return total


def calculate_mission_stats(grid, waypoints):
    """
    Calculate performance metrics for a grid mission.
    
    Args:
        grid: GridMission instance
        waypoints: List of generated waypoints
        
    Returns:
        dict with performance metrics
    """
    # Number of tracks (exclude takeoff and landing waypoints)
    num_grid_waypoints = len(waypoints)
    num_tracks = num_grid_waypoints // 2  # 2 waypoints per track
    
    # Total distance
    total_distance = calculate_total_distance(waypoints)
    
    # Estimated time (assuming 5 m/s average cruise speed)
    avg_speed = 5.0  # m/s
    flight_time_sec = total_distance / avg_speed

    # Hover time at each waypoint for photo capture
    hover_per_waypoint = 3.0  # seconds (matches your grid_flight.py sleep(3))
    hover_time_sec = num_grid_waypoints * hover_per_waypoint

    # Overhead (takeoff, landing, initial positioning)
    overhead_sec = 60.0  # ~1 minute

    # Total mission time
    estimated_time_sec = flight_time_sec + hover_time_sec + overhead_sec
    estimated_time_min = estimated_time_sec / 60
    
    # Coverage area
    coverage_area = grid.width * grid.length
    
    # Efficiency (area covered per minute)
    efficiency = coverage_area / estimated_time_min if estimated_time_min > 0 else 0
    
    # Battery estimate (2% per minute based on yesterday's data)
    battery_usage = estimated_time_min * 2.0
    
    return {
        'waypoints': num_grid_waypoints,
        'tracks': num_tracks,
        'distance': total_distance,
        'time_sec': estimated_time_sec,
        'time_min': estimated_time_min,
        'area': coverage_area,
        'efficiency': efficiency,
        'battery_est': battery_usage
    }


def run_test_suite():
    """Run all grid configuration tests."""
    
    # Test configurations: (width, length, altitude, spacing, name)
    configs = [
        (20, 20, 15, 5, "Small_HighDetail"),
        (50, 50, 15, 10, "Medium_Standard"),
        (100, 100, 15, 12, "Large_Efficient"),
        (100, 100, 20, 15, "Large_HighFast"),
        (200, 200, 15, 10, "XL_Detailed"),
    ]
    
    results = []
    
    print("\n" + "="*90)
    print("GRID CONFIGURATION TEST SUITE")
    print("="*90 + "\n")
    
    for width, length, altitude, spacing, name in configs:
        print(f"Testing: {name}...")
        
        # Create grid mission
        grid = GridMission(
            center=(0, 0),
            width=width,
            length=length,
            altitude=altitude,
            spacing=spacing
        )
        
        # Generate waypoints
        waypoints = grid.generate()
        
        # Calculate stats
        stats = calculate_mission_stats(grid, waypoints)
        
        # Combine config and stats
        result = {
            'name': name,
            'width': width,
            'length': length,
            'altitude': altitude,
            'spacing': spacing,
            **stats  # Unpack stats dict
        }
        
        results.append(result)
        print(f"  ✓ {stats['waypoints']} waypoints, {stats['tracks']} tracks, "
              f"{stats['distance']:.0f}m, {stats['time_min']:.1f}min")
    
    print()
    return results


def print_comparison_table(results):
    """Print formatted comparison table."""
    
    print("="*90)
    print("PERFORMANCE COMPARISON")
    print("="*90)
    print(f"{'Config':<18} {'Area':<8} {'Alt':<5} {'Spc':<5} {'Trks':<5} "
          f"{'Dist':<8} {'Time':<8} {'Batt':<6} {'Effic':<10}")
    print(f"{'Name':<18} {'(m²)':<8} {'(m)':<5} {'(m)':<5} {'(#)':<5} "
          f"{'(m)':<8} {'(min)':<8} {'(%)':<6} {'(m²/min)':<10}")
    print("-"*90)
    
    for r in results:
        print(f"{r['name']:<18} {r['area']:<8.0f} {r['altitude']:<5.0f} "
              f"{r['spacing']:<5.0f} {r['tracks']:<5} {r['distance']:<8.0f} "
              f"{r['time_min']:<8.1f} {r['battery_est']:<6.1f} {r['efficiency']:<10.1f}")
    
    print("="*90)
    
    # Analysis
    print("\nKEY INSIGHTS:")
    
    # Most efficient
    most_efficient = max(results, key=lambda x: x['efficiency'])
    print(f"✓ Most Efficient: {most_efficient['name']} "
          f"({most_efficient['efficiency']:.1f} m²/min)")
    
    # Fastest per area
    fastest = min(results, key=lambda x: x['time_min'] / x['area'])
    print(f"✓ Fastest Coverage Rate: {fastest['name']} "
          f"({fastest['area']/fastest['time_min']:.1f} m²/min)")
    
    # Battery considerations
    single_battery = [r for r in results if r['battery_est'] < 50]
    print(f"✓ Single Battery Capable: {len(single_battery)}/{len(results)} configs")
    
    print("\nRECOMMENDATIONS:")
    print("• Small Roofs (<1000m²): Use 'Small_HighDetail' or 'Medium_Standard'")
    print("• Large Buildings (>5000m²): Use 'Large_Efficient' or 'Large_HighFast'")
    print("• Battery Constraints: Increase altitude and spacing to reduce flight time")
    print("• 3D Mapping: Use smaller spacing (5m) for 70% overlap")
    print()


def save_results_csv(results, filename=None):
    """Save results to CSV file."""
    
    if filename is None:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'logs/grid_test_results_{timestamp}.csv'
    
    fieldnames = [
    'name', 'width', 'length', 'altitude', 'spacing',
    'waypoints', 'tracks', 'distance', 'time_sec', 'time_min',
    'area', 'efficiency', 'battery_est'
    ]
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✓ Results saved to: {filename}\n")
    return filename


def main():
    """Run complete test suite."""
    
    # Run tests
    results = run_test_suite()
    
    # Print comparison
    print_comparison_table(results)
    
    # Save to CSV
    csv_file = save_results_csv(results)
    
    print("="*90)
    print("TEST SUITE COMPLETE")
    print("="*90)


if __name__ == "__main__":
    main()