from grid_mission import GridMission
from first_flight import (connect_to_vehicle, print_timestamped, set_target_position,
                         wait_for_setpoints_active, arm, set_mode, start_setpoint_thread,
                         stop_setpoint_thread, wait_for_position, preflight_checks)
import constants 
from pymavlink import mavutil
from datetime import datetime
import threading
import math
from time import time, sleep
from telemetry_logging import TelemetryLogger
import sys


def apply_flight_profile(connection, system_id, component_id, profile):
    """Apply flight profile parameters to PX4."""
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


def main():
    # ========================================
    # FLIGHT PROFILE SELECTION
    # ========================================
    FLIGHT_PROFILE = "efficient"  # Options: "aggressive", "efficient", "conservative"
    
    profiles = {
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
    
    current_profile = profiles[FLIGHT_PROFILE]
    
    print_timestamped(f"\n{'='*60}")
    print_timestamped(f"FLIGHT PROFILE: {FLIGHT_PROFILE.upper()}")
    print_timestamped(f"Description: {current_profile['description']}")
    print_timestamped(f"Max Speed: {current_profile['max_speed']} m/s")
    print_timestamped(f"Max Accel: {current_profile['max_accel']} m/s²")
    print_timestamped(f"{'='*60}\n")
    
    # 1. Create mission
    grid = GridMission(
        center=(0, 0),
        width=100,  # Smaller for testing
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
    
    # 2. Telemetry logger (with profile name)
    logger = TelemetryLogger(flight_profile=FLIGHT_PROFILE)
    
    # 3. Connect to vehicle
    connection = connect_to_vehicle(constants.CONNECTION_STRING)
    system_id = connection.target_system
    component_id = connection.target_component
    
    # 3.5 Apply flight profile
    apply_flight_profile(connection, system_id, component_id, current_profile)
    print_timestamped("Waiting for parameters to settle...")
    sleep(5)
    
    # 4. Pre-flight checks
    if not preflight_checks(connection):
        print_timestamped("✗ Pre-flight checks failed - ABORTING")
        return
    print_timestamped("✓ Pre-flight checks passed")
    
    try:
        # 5. Start setpoint thread
        set_target_position(constants.TARGET_POSITION_GROUND[0],
                           constants.TARGET_POSITION_GROUND[1],
                           constants.TARGET_POSITION_GROUND[2])
        start_setpoint_thread(connection=connection, system_id=system_id, component_id=component_id)
        sleep(2)
        
        if not wait_for_setpoints_active(connection):
            print_timestamped("✗ Setpoints not being received by PX4")
            return
        
        # 6. Arm
        if not arm(connection, system_id, component_id):
            print_timestamped("✗ Failed to arm")
            return
        
        sleep(3)
        
        # 7. OFFBOARD mode
        if not set_mode(connection, system_id, component_id, 6):
            print_timestamped("✗ Failed to enter OFFBOARD mode - ABORTING")
            return
        
        sleep(3)
        
        # 8. Start logging
        logger.start_logging(connection=connection)
        
        # 9. Execute mission
        for i, waypoint in enumerate(mission):
            x, y, z = waypoint
            logger.set_waypoint(i)  
            logger.set_target(x, y, z)
            print_timestamped(f"\n=== Waypoint {i+1}/{len(mission)} ===")
            set_target_position(x, y, z)
            wait_for_position(connection, x, y, z)
            sleep(3)
            
    finally:
        logger.stop_logging()
        csv_path = logger.save_to_csv()
        
        # Generate visualizations
        if csv_path:
            print_timestamped("\nGenerating flight visualizations...")
            sys.path.append('../analysis')
            from visualize_flight import visualize_flight
            visualize_flight(csv_path, output_dir='../analysis/plots')
        
        stop_setpoint_thread()
        connection.close()
        print_timestamped('Connection closed!')

        
if __name__ == "__main__":
    main()