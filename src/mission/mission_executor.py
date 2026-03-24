"""
Mission Executor - Autonomous Grid Flight

Main script for executing grid inspection missions with OFFBOARD control.
Refactored from grid_flight.py with modular architecture.
"""

import sys
import os
from time import sleep
from pymavlink import mavutil

# Core imports
from src.core.connection import connect_to_vehicle, print_timestamped, preflight_checks
from src.core.flight_controller import (
    set_target_position, wait_for_setpoints_active, arm, set_mode,
    start_setpoint_thread, stop_setpoint_thread
)
from src.core.navigation import wait_for_position
from src.core import constants

# Mission imports
from src.mission.grid_planner import GridMission

# Sensor imports
from src.sensors.telemetry import TelemetryLogger
from src.sensors.camera import trigger_camera, cleanup_camera_images


# Configuration
GENERATE_ENHANCED_REPORT = True


def apply_flight_profile(connection, system_id, component_id, profile):
    """
    Apply flight profile parameters to PX4.
    
    Args:
        connection: MAVLink connection
        system_id: Target system ID
        component_id: Target component ID
        profile: Profile dict with speed/accel params
    """
    print_timestamped("Applying flight profile parameters...")
    
    params_to_set = {
        'MPC_XY_VEL_MAX': profile['max_speed'],
        'MPC_XY_CRUISE': profile['cruise_speed'],
        'MPC_ACC_HOR_MAX': profile['max_accel'],
        'MPC_ACC_HOR': profile['accel'],
    }
    
    for param_name, param_value in params_to_set.items():
        connection.mav.param_set_send(
            system_id,
            component_id,
            param_name.encode('utf-8'),
            param_value,
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )
        sleep(0.1)
    
    print_timestamped(f"✓ Profile applied: max_speed={profile['max_speed']} m/s, "
                      f"max_accel={profile['max_accel']} m/s²")


def get_flight_profiles():
    """
    Define available flight profiles.
    
    Returns:
        dict: Flight profiles with speed/accel parameters
    """
    return {
        "aggressive": {
            "max_speed": 12.0,
            "cruise_speed": 10.0,
            "max_accel": 10.0,
            "accel": 8.0,
            "description": "Fast, high battery consumption"
        },
        "efficient": {
            "max_speed": 6.0,
            "cruise_speed": 5.0,
            "max_accel": 3.0,
            "accel": 2.0,
            "description": "Balanced speed and battery efficiency (RECOMMENDED)"
        },
        "conservative": {
            "max_speed": 3.0,
            "cruise_speed": 2.5,
            "max_accel": 1.5,
            "accel": 1.0,
            "description": "Maximum battery efficiency, slow"
        }
    }


def execute_mission(connection, system_id, component_id, mission, logger):
    """
    Execute mission waypoints.
    
    Args:
        connection: MAVLink connection
        system_id: Target system ID
        component_id: Target component ID
        mission: List of (x, y, z) waypoints
        logger: TelemetryLogger instance
    """
    for i, waypoint in enumerate(mission):
        x, y, z = waypoint
        logger.set_waypoint(i)
        logger.set_target(x, y, z)
        
        print_timestamped(f"\n=== Waypoint {i+1}/{len(mission)} ===")
        set_target_position(x, y, z)
        
        reached, _ = wait_for_position(connection, x, y, z)
        
        if reached:
            trigger_camera(connection, system_id, component_id, i+1)
            sleep(1)
        
        sleep(3)


def post_flight_processing(csv_path):
    """
    Generate visualizations and reports after flight.
    
    Args:
        csv_path: Path to telemetry CSV file
    """
    print_timestamped("\n" + "="*60)
    print_timestamped("POST-FLIGHT PROCESSING")
    print_timestamped("="*60)
    
    # 1. Generate visualizations
    print_timestamped("\n[1/2] Generating flight visualizations...")
    plot_dir = None
    try:
        from src.processing.visualization import visualize_flight
        plot_dir = visualize_flight(csv_path, output_dir='data/outputs/plots')
        if plot_dir:
            print_timestamped(f"✓ Plots saved to: {plot_dir}")
    except Exception as e:
        print_timestamped(f"✗ Visualization failed: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. Generate PDF report
    print_timestamped("\n[2/2] Generating PDF report...")
    report_path = None
    try:
        if GENERATE_ENHANCED_REPORT:
            from src.reporting.technical_report import EnhancedFlightReportGenerator
            generator = EnhancedFlightReportGenerator(csv_path, output_dir='data/outputs/reports')
            report_path = generator.generate_enhanced_report()
        else:
            from src.reporting.client_report import FlightReportGenerator
            generator = FlightReportGenerator(csv_path, output_dir='data/outputs/reports')
            report_path = generator.generate_technical_report()
        
        if report_path:
            print_timestamped(f"✓ Report saved to: {report_path}")
    except Exception as e:
        print_timestamped(f"✗ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Clean up camera images
    cleanup_camera_images()
    
    # Summary
    print_timestamped("\n" + "="*60)
    print_timestamped("✓ POST-FLIGHT PROCESSING COMPLETE")
    print_timestamped("="*60)
    print_timestamped(f"\nFlight Data:    {csv_path}")
    if plot_dir:
        print_timestamped(f"Visualizations: {plot_dir}")
    if report_path:
        print_timestamped(f"PDF Report:     {report_path}")
    print_timestamped("="*60 + "\n")


def main():
    """Main mission execution function."""
    
    # ========================================
    # FLIGHT PROFILE SELECTION
    # ========================================
    FLIGHT_PROFILE = "efficient"  # Options: "aggressive", "efficient", "conservative"
    
    profiles = get_flight_profiles()
    current_profile = profiles[FLIGHT_PROFILE]
    
    print_timestamped(f"\n{'='*60}")
    print_timestamped(f"FLIGHT PROFILE: {FLIGHT_PROFILE.upper()}")
    print_timestamped(f"Description: {current_profile['description']}")
    print_timestamped(f"Max Speed: {current_profile['max_speed']} m/s")
    print_timestamped(f"Max Accel: {current_profile['max_accel']} m/s²")
    print_timestamped(f"{'='*60}\n")
    
    # ========================================
    # MISSION PLANNING
    # ========================================
    grid = GridMission(
        center=(0, 0),
        width=100,
        length=100,
        altitude=15,
        spacing=10
    )
    waypoints = grid.generate()
    mission = [
        (0, 0, -15),  # takeoff
        *waypoints,
        constants.TARGET_POSITION_GROUND  # landing
    ]
    
    print_timestamped(f"\n{'='*60}")
    print_timestamped("GRID MISSION PLAN")
    print_timestamped(f"{'='*60}")
    print_timestamped(f"Grid: {grid.width}m × {grid.length}m at {grid.altitude}m altitude")
    print_timestamped(f"Track spacing: {grid.spacing}m")
    print_timestamped(f"Total waypoints: {len(mission)}")
    print_timestamped(f"  - Takeoff: 1")
    print_timestamped(f"  - Grid pattern: {len(waypoints)}")
    print_timestamped(f"  - Landing: 1")
    print_timestamped(f"{'='*60}\n")
    
    # ========================================
    # SETUP
    # ========================================
    logger = TelemetryLogger(flight_profile=FLIGHT_PROFILE)
    connection = connect_to_vehicle(constants.CONNECTION_STRING)
    
    print_timestamped("Waiting for GPS lock...")
    sleep(10)
    
    system_id = connection.target_system
    component_id = connection.target_component
    
    # Apply flight profile
    apply_flight_profile(connection, system_id, component_id, current_profile)
    print_timestamped("Waiting for parameters to settle...")
    sleep(5)
    
    # Pre-flight checks
    if not preflight_checks(connection):
        print_timestamped("✗ Pre-flight checks failed - ABORTING")
        return
    print_timestamped("✓ Pre-flight checks passed")
    
    # ========================================
    # FLIGHT EXECUTION
    # ========================================
    try:
        # Start setpoint thread
        set_target_position(
            constants.TARGET_POSITION_GROUND[0],
            constants.TARGET_POSITION_GROUND[1],
            constants.TARGET_POSITION_GROUND[2]
        )
        start_setpoint_thread(connection=connection, system_id=system_id, component_id=component_id)
        sleep(2)
        
        if not wait_for_setpoints_active(connection):
            print_timestamped("✗ Setpoints not being received by PX4")
            return
        
        # Arm
        if not arm(connection, system_id, component_id):
            print_timestamped("✗ Failed to arm")
            return
        
        sleep(3)
        
        # OFFBOARD mode
        if not set_mode(connection, system_id, component_id, 6):
            print_timestamped("✗ Failed to enter OFFBOARD mode - ABORTING")
            return
        
        sleep(3)
        
        # Start logging
        logger.start_logging(connection=connection)
        
        # Execute mission
        execute_mission(connection, system_id, component_id, mission, logger)
        
    finally:
        # Stop logging and save
        logger.stop_logging()
        csv_path = logger.save_to_csv()
        
        # Post-flight processing
        if csv_path:
            post_flight_processing(csv_path)
        
        # Cleanup
        stop_setpoint_thread()
        connection.close()
        print_timestamped('Connection closed!')


if __name__ == "__main__":
    main()