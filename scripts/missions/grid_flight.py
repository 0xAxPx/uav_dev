from grid_mission import GridMission
from first_flight import connect_to_vehicle, print_timestamped,set_target_position,wait_for_setpoints_active,arm,set_mode, start_setpoint_thread, stop_setpoint_thread, wait_for_position, preflight_checks
import constants 
from pymavlink import mavutil
from datetime import datetime
import threading
import math
from time import time, sleep
from telemetry_logging import TelemetryLogger
from analysis.visualize_flight import visualize_flight
import sys


def main():
    # 1. Create mission
    grid = GridMission(
        center=(0, 0),
        width=200,
        length=200,
        altitude=15,
        spacing=10
    )
    waypoints = grid.generate()
    mission = [
        (0,0,-15),# take off
        *waypoints,
        constants.TARGET_POSITION_GROUND # landing
    ]
    
    print_timestamped(f"\n{'='*60}")
    print_timestamped("GRID MISSION PLAN")
    print_timestamped(f"{'='*60}")
    print_timestamped(f"Grid: {grid.width}m × {grid.length}m at {grid.altitude}m altitude")
    print_timestamped(f"Track spacing: {grid.spacing}m")
    print_timestamped(f"Total waypoints: {len(mission)}")
    print_timestamped("  - Takeoff: 1")
    print_timestamped(f"  - Grid pattern: {len(waypoints)}")
    print_timestamped("  - Landing: 1")
    print_timestamped(f"{'='*60}\n")
    
    # 2. Telemetry logger
    logger = TelemetryLogger()
    
    # 3. Connect to vehicle
    connection=connect_to_vehicle(constants.CONNECTION_STRING)
    system_id=connection.target_system
    component_id=connection.target_component
    
    # 4. Pre-flight checks
    if not preflight_checks(connection):
        print_timestamped("✗ Pre-flight checks failed - ABORTING")
        return
    print_timestamped("✓ Pre-flight checks passed")
    
    try:
        # 5. Start setpoint thread at ground level
        set_target_position(constants.TARGET_POSITION_GROUND[0], constants.TARGET_POSITION_GROUND[1], constants.TARGET_POSITION_GROUND[2])
        start_setpoint_thread(connection=connection, system_id=system_id, component_id=component_id)
        sleep(2)
        
        if not wait_for_setpoints_active(connection):
            print_timestamped("✗ Setpoints not being received by PX4")
            return
        
        # 6. Check if it is armed
        if not arm(connection, system_id, component_id):
            print_timestamped("✗ Failed to arm")
            return
        
        sleep(3)
        
        # 7. OFFBOARD mode with verification
        if not set_mode(connection, system_id, component_id, 6):
            print_timestamped("✗ Failed to enter OFFBOARD mode - ABORTING")
            return
        
        # 8. Start logger
        logger.start_logging(connection=connection)
        
        # 8. Execute mission 
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
        logger.save_to_csv()
        
        print_timestamped("\nGenerating flight visualizations...")
        sys.path.append('../analysis')
        visualize_flight(csv_path, output_dir='../analysis/plots')
        
        stop_setpoint_thread()
        connection.close()
        print_timestamped('Connection closed!')
        

if __name__ == "__main__":
    main()