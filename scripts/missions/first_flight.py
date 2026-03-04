from pymavlink import mavutil
from datetime import datetime
from time import sleep
from time import time
import threading
import math
from time import time, sleep


# Shared state
target_position = {
    'x': 0.0,
    'y': 0.0,
    'z': 0.0
}

setpoint_thread_running = False
setpoint_thread = None

# Constants
CONNECTION_STRING = "udp:127.0.0.1:14540"
MSG_HEARTBEAT = "HEARTBEAT"
MSG_ACK = "COMMAND_ACK"
MSG_GPS = "GPS_RAW_INT"
MSG_SYS = "SYS_STATUS"
MSG_HUD = "VFR_HUD"
MSG_LOC_POSIT_NED = "LOCAL_POSITION_NED"


def print_timestamped(message):
    """Print message with timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}")
    
def send_sentpoint_thread(connection, system_id, component_id):
    """
    Background thread that continuously sends position setpoints.
    Runs at 20Hz (every 50ms) to meet PX4's >2Hz requirement.
    """
    
    global setpoint_thread_running, target_position
    
    while setpoint_thread_running:
        connection.mav.send(
            mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
                10,  # time_boot_ms
                system_id,
                component_id,
                mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                int(0b0000111111111000),  # type_mask
                target_position['x'],
                target_position['y'],
                target_position['z'],
                0, 0, 0,  # velocities
                0, 0, 0,  # accelerations
                0, 0      # yaw, yaw_rate
            )
        )        
        sleep(0.05) #50ms == 20Hz

def start_setpoint_thread(connection, system_id, component_id):
    """Start the background setpoint sender thread."""
    global setpoint_thread_running, setpoint_thread
    
    setpoint_thread_running = True
    setpoint_thread = threading.Thread(
        target=send_sentpoint_thread,
        args=(connection, system_id, component_id),
        daemon=True
    )
    setpoint_thread.start()
    print_timestamped("Setpoint thread started with 20HZ")

def stop_setpoint_thread():
    """Stop the background setpoint sender thread."""
    global setpoint_thread_running, setpoint_thread
    
    setpoint_thread_running = False
    if setpoint_thread:
        setpoint_thread.join(timeout=2.0) # Wait for thread to finish 
    print_timestamped("Setpoint thread stopped!")
    

# Get current position
def get_current_position(connection, timeout=2):
    """
    Get drone's current position from LOCAL_POSITION_NED message.
    
    Args:
        connection: MAVLink connection object
        timeout: How long to wait for message (seconds)
    
    Returns:
        dict: {'x': float, 'y': float, 'z': float, 'timestamp': int}
        None: If timeout or no message received
    """
    
    msg = connection.recv_match(type=MSG_LOC_POSIT_NED, blocking=True, timeout=timeout)
    if msg:
        position = {
            'x': msg.x,
            'y': msg.y,
            'z': msg.z,
            'vx': msg.vx,
            'vy': msg.vy,
            'vz': msg.vz,
            'timestamp': msg.time_boot_ms
        }
        
        # Add computed fields
        position['altitude'] = -msg.z  # Convert down to altitude
        position['ground_speed'] = math.sqrt(msg.vx**2 + msg.vy**2)
        position['vertical_speed'] = -msg.vz  # Negative = climbing
            
        return position
        
    return None

# Get altitude
def get_current_altitude(connection, timeout=2):
    position=get_current_position(connection=connection, timeout=timeout)
    return position['altitude'] if position else None

# Get altitude
def get_current_ground_speed(connection, timeout=2):
    position=get_current_position(connection=connection, timeout=timeout)
    return position['ground_speed'] if position else None

# Get altitude
def get_current_vertical_speed(connection, timeout=2):
    position=get_current_position(connection=connection, timeout=timeout)
    return position['vertical_speed'] if position else None    

# Get vertical position
def get_position_xy(connection, timeout=2):
    """
    Get just horizontal position (useful for waypoint checks).
    Returns: (x, y) tuple or None
    """
    pos = get_current_position(connection, timeout)
    return (pos['x'], pos['y']) if pos else None

# 3D distance
def distance_3d(pos1, pos2):
    """
    Calculate 3D distance between two positions.
    
    Args:
        pos1: dict with 'x', 'y', 'z' keys
        pos2: dict with 'x', 'y', 'z' keys
    
    Returns:
        float: Distance in meters
    """
    dx = pos2['x'] - pos1['x']
    dy = pos2['y'] - pos1['y'] 
    dz = pos2['z'] - pos1['z']
    return math.sqrt(dx**2 + dy**2 + dz**2)    

# Horizontal distance
def horizontal_distance(pos1, pos2):
    """
    Calculate horizontal distance (XY plane only).
    
    Args:
        pos1: dict with 'x', 'y' keys
        pos2: dict with 'x', 'y' keys
    
    Returns:
        float: Horizontal distance in meters
    """
    dx = pos2['x'] - pos1['x']
    dy = pos2['y'] - pos1['y']
    return math.sqrt(dx**2 + dy**2)

# Get altitude
def altitude_difference(pos1, pos2):
    """
    Calculate altitude difference (absolute value).
    Handles both 'altitude' and 'z' keys properly.
    """
    # Get altitude for pos1 (prefer 'altitude', fallback to '-z')
    if 'altitude' in pos1:
        alt1 = pos1['altitude']
    else:
        alt1 = -pos1.get('z', 0)
    
    # Get altitude for pos2 (prefer 'altitude', fallback to '-z')
    if 'altitude' in pos2:
        alt2 = pos2['altitude']
    else:
        alt2 = -pos2.get('z', 0)
    
    return abs(alt2 - alt1)

def wait_for_position(connection, target_x, target_y, target_z,
                     tolerance_xy=1.0, tolerance_z=0.5, 
                     timeout=30, check_interval=0.2):
    """
    Wait until drone reaches target position within tolerance.
    
    Args:
        connection: MAVLink connection
        target_x: Target North position (m)
        target_y: Target East position (m)
        target_z: Target Down position (m, negative = altitude)
        tolerance_xy: Horizontal acceptance radius (m)
        tolerance_z: Vertical acceptance radius (m)
        timeout: Maximum wait time (seconds)
        check_interval: How often to check position (seconds)
    
    Returns:
        bool: True if position reached, False if timeout
        dict: Final position when function returns
    """
    start_time = time()
    target_pos = {'x': target_x, 'y': target_y, 'z': target_z, 'altitude': -target_z}
    
    print_timestamped(f"Waiting for position: N={target_x:.1f}m, "
                     f"E={target_y:.1f}m, Altitude={-target_z:.1f}m")
    print_timestamped(f"Tolerance: XY={tolerance_xy}m, Z={tolerance_z}m")
    
    while (time() - start_time) < timeout:
        # Get current position
        current_pos = get_current_position(connection, timeout=2)
        
        if not current_pos:
            print_timestamped("Warning: No position data received")
            sleep(check_interval)
            continue
        
        # Calculate distances
        dist_xy = horizontal_distance(current_pos, target_pos)
        dist_z = altitude_difference(current_pos, target_pos)
        
        # Check if within tolerance
        xy_reached = dist_xy <= tolerance_xy
        z_reached = dist_z <= tolerance_z
        
        # Print progress every second
        elapsed = time() - start_time
        if int(elapsed) != int(elapsed - check_interval):  # Print once per second
            print_timestamped(
                f"Distance: XY={dist_xy:.2f}m [{('✓' if xy_reached else '✗')}], "
                f"Z={dist_z:.2f}m [{('✓' if z_reached else '✗')}]"
            )
        
        # Success condition: both horizontal and vertical within tolerance
        if xy_reached and z_reached:
            print_timestamped(f"✓ Position reached! (took {elapsed:.1f}s)")
            return True, current_pos
        
        sleep(check_interval)
    
    # Timeout
    print_timestamped(f"✗ Timeout after {timeout}s")
    final_pos = get_current_position(connection, timeout=1)
    return False, final_pos


def wait_for_position_stable(connection, target_x, target_y, target_z,
                             tolerance_xy=1.0, tolerance_z=0.5,
                             max_speed=0.5, stability_time=1.0,
                             timeout=30, check_interval=0.2):
    """
    Wait for position with stability check (position + low speed).
    
    Args:
        max_speed: Maximum ground speed to consider "stable" (m/s)
        stability_time: How long to remain stable (seconds)
        ... (other args same as wait_for_position)
    
    Returns:
        bool: True if stable position reached, False if timeout
        dict: Final position
    """
    start_time = time()
    stable_since = None  # Track when stability started
    target_pos = {'x': target_x, 'y': target_y, 'z': target_z}
    
    print_timestamped(f"Waiting for STABLE position: N={target_x:.1f}m, "
                     f"E={target_y:.1f}m, D={target_z:.1f}m")
    print_timestamped(f"Tolerance: XY={tolerance_xy}m, Z={tolerance_z}m, "
                     f"Speed<{max_speed}m/s for {stability_time}s")
    
    while (time() - start_time) < timeout:
        current_pos = get_current_position(connection, timeout=2)
        
        if not current_pos:
            stable_since = None  # Reset stability
            sleep(check_interval)
            continue
        
        # Calculate distances and speed
        dist_xy = horizontal_distance(current_pos, target_pos)
        dist_z = altitude_difference(current_pos, target_pos)
        ground_speed = current_pos.get('ground_speed', 999)
        
        # Check conditions
        xy_reached = dist_xy <= tolerance_xy
        z_reached = dist_z <= tolerance_z
        speed_ok = ground_speed <= max_speed
        
        is_stable = xy_reached and z_reached and speed_ok
        
        if is_stable:
            if stable_since is None:
                stable_since = time()
                print_timestamped("Position reached, waiting for stability...")
            
            stable_duration = time() - stable_since
            
            if stable_duration >= stability_time:
                elapsed = time() - start_time
                print_timestamped(f"✓ Stable position reached! (took {elapsed:.1f}s)")
                return True, current_pos
        else:
            stable_since = None  # Reset if conditions no longer met
        
        # Print progress
        elapsed = time() - start_time
        if int(elapsed) != int(elapsed - check_interval):
            status = "STABLE" if is_stable else "MOVING"
            print_timestamped(
                f"[{status}] XY={dist_xy:.2f}m, Z={dist_z:.2f}m, "
                f"Speed={ground_speed:.2f}m/s"
            )
        
        sleep(check_interval)
    
    print_timestamped(f"✗ Timeout after {timeout}s")
    final_pos = get_current_position(connection, timeout=1)
    return False, final_pos

def set_target_position(x, y, z):
    """
    Update the target position that the setpoint thread is sending.
    This is called from your main thread to command movement.
    
    NED coordinates
    - x: North (positive = north, negative = south)
    - y: East (positive = east, negative = west)
    - z: Down (positive = down, NEGATIVE = up!)
    """
    global target_position
    target_position['x'] = x
    target_position['y'] = y
    target_position['z'] = z
    print_timestamped(f"Target updated: N={x}m, E={y}m, D={z}m")
    

def connect_to_vehicle(connection_string):
    """
    Connect to vehicle and wait for heartbeat.
    Returns connection object.
    """
    print_timestamped(f"Connecting to vehicle on {connection_string}...")
    connection = mavutil.mavlink_connection(connection_string)
    connection.wait_heartbeat()
    
    print_timestamped(
        f"Connected! System {connection.target_system} "
        f"Component {connection.target_component} "
        f"Mode: {connection.flightmode}"
    )
    return connection

def arm(connection, system_id, component_id):
    connection.mav.command_long_send(
        system_id,
        component_id,
        400,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0
    )
    
    # get acknowledgment
    ack_msg = connection.recv_match(type=MSG_ACK, blocking=True, timeout = 5)
    if not ack_msg:
        return None
    if ack_msg and ack_msg.command == 400:
        # result == 0 (accepted)
        if ack_msg.result == 0:
            print_timestamped(f'ACK:{ack_msg}')
            print_timestamped("Armed!")
            return True
        else:
            print_timestamped(f'There is a problem with getting {MSG_ACK} for arming drone, result returned = {ack_msg.result}')
    else:
        print_timestamped('Arm failed!')
        return False

def set_mode(connection, system_id, component_id, mode_name):
    print_timestamped(f'Setting flight mode to {mode_name}')
    if mode_name == 'OFFBOARD' or mode_name == 6:
        connection.mav.command_long_send(
            system_id,
            component_id,
            176,
            0,
            1,
            6,
            0,
            0,0,0,0
        )
    
    ack_msg = connection.recv_match(type=MSG_ACK, blocking=True, timeout=5)
    
    if not ack_msg:
        print_timestamped("No ACK received for mode change")
        return False
        
    if ack_msg.command == 176:
        if ack_msg.result == 0:
            print_timestamped(f'ACK:{ack_msg}')
            print_timestamped('Flight mode command accepted')
            
            # Wait longer and check multiple heartbeats
            sleep(2)
            
            # Check heartbeat multiple times (sometimes takes a moment)
            for attempt in range(3):
                heartbeat = connection.recv_match(type=MSG_HEARTBEAT, blocking=True, timeout=2)
                if heartbeat:
                    main_mode = (heartbeat.custom_mode >> 16) & 0xFF
                    print_timestamped(f"Attempt {attempt+1}: Mode = {main_mode}")
                    
                    if main_mode == 6:
                        print_timestamped("✓ Drone is now in OFFBOARD mode")
                        return True
                
                sleep(1)  # Wait between attempts
            
            # If we get here, mode never changed
            print_timestamped("✗ Failed to enter OFFBOARD mode after 3 attempts")
            return False
        else:
            print_timestamped(f'Mode change rejected, result: {ack_msg.result}')
            return False
    
    return False

def wait_for_setpoints_active(connection, timeout=10):
    """
    Wait until PX4 acknowledges receiving setpoints.
    This ensures OFFBOARD mode will work.
    """
    print_timestamped("Waiting for PX4 to acknowledge setpoints...")
    start_time = time()
    
    while (time() - start_time) < timeout:
        # Check if we're getting position target feedback
        pos_target = connection.recv_match(
            type='POSITION_TARGET_LOCAL_NED',
            blocking=True,
            timeout=1
        )
        
        if pos_target:
            print_timestamped("✓ PX4 is receiving setpoints")
            return True
        
        sleep(0.5)
    
    print_timestamped("✗ PX4 not acknowledging setpoints")
    return False

def takeoff(connection, system_id, component_id, height):
    print_timestamped(f'Taking off drone at {height} height')
    connection.mav.command_long_send(
        system_id,
        component_id,
        22,
        0,
        0,0,0,0,
        0,0,
        height
    )
    
    ack_msg = connection.recv_match(type=MSG_ACK, blocking=True, timeout = 5)
    if not ack_msg:
        return None
    if ack_msg and ack_msg.command == 22:
        if ack_msg.result == 0:
            print_timestamped(f'ACK:{ack_msg}')
            print_timestamped(f'Drone is hovering at {height} meters!')
            return True
        else:
            print_timestamped(f'There is a problem with getting {MSG_ACK} for taking off, result returned = {ack_msg.result}')
    else:
        print_timestamped('Drone takeoff failed!')
        return False


def land(connection, system_id, component_id):
    connection.mav.command_long_send(
        system_id,
        component_id,
        21,
        0,
        0,0,0,0,
        0,0,
        0
    )
    ack_msg = connection.recv_match(type=MSG_ACK, blocking=True, timeout = 5)
    if not ack_msg:
        return None
    if ack_msg and ack_msg.command == 21:
        if ack_msg.result == 0:
            print_timestamped(f'ACK:{ack_msg}')
            print_timestamped('Drone landed successfully!')
            return True
        else:
            print_timestamped(f'There is a problem with getting {MSG_ACK} for drone landing, result returned = {ack_msg.result}')

    else:
        print_timestamped('Drone landing failed!')
        return False
    

def wait_for_altitude(connection, target_alt, tolerance = 0.5):
    start_time = time()
    timeout = 30
    while (time() - start_time) < timeout:
        msg = connection.recv_match(type=MSG_HUD, blocking = True, timeout = 2)
        if msg:
            current_alt = msg.alt
            
            if abs(current_alt - target_alt) < tolerance:
                print_timestamped(f'Reached altitude {current_alt}m')
                return True
        sleep(0.1)
    print_timestamped("Timeout waiting for altitude")
    return False
            
    
def main():
    connection = connect_to_vehicle(CONNECTION_STRING)
    system_id = connection.target_system
    component_id = connection.target_component
    
    # pre-flight checks
    gps_msg = connection.recv_match(type=MSG_GPS, blocking=True, timeout=2)
    if not gps_msg:
        return None
    gps_fix_type = gps_msg.fix_type
    
    sys_status_msg = connection.recv_match(type=MSG_SYS, blocking=True, timeout=3)
    if not sys_status_msg:
        return None
    battery_remaining = sys_status_msg.battery_remaining
    
    # Check if GPS 3D position and battery is more than 30% charge
    if gps_fix_type != 3 or battery_remaining <= 30:
        return False
    else:
        print_timestamped(f'Pre-flight checks passed. Battery remain = {battery_remaining}, GPS fix type = {gps_fix_type}')
    
    try:
        # Start setpoint thread at ground level
        set_target_position(0, 0, 0)
        start_setpoint_thread(connection=connection, system_id=system_id, component_id=component_id)
        sleep(2)
        
        if not wait_for_setpoints_active(connection, timeout=10):
            print_timestamped("✗ Setpoints not being received by PX4")
            return
        
        # Arm and enter OFFBOARD mode
        if not arm(connection, system_id, component_id):
            print_timestamped("✗ Failed to arm")
            return
        
        sleep(3)
        
        # Set OFFBOARD mode (with proper verification)
        if not set_mode(connection, system_id, component_id, 6):
            print_timestamped("✗ Failed to enter OFFBOARD mode - ABORTING")
            return
            
        # ========================================
        # MISSION WAYPOINTS WITH VERIFICATION
        # ========================================
            
        # Waypoint 1: Takeoff to 5m
        print_timestamped("\n=== WAYPOINT 1: Takeoff to 5m ===")
        set_target_position(0, 0, -5.0)
        reached, pos = wait_for_position(
            connection, 0, 0, -5.0,
            tolerance_xy=1.0,
            tolerance_z=0.5,
            timeout=50
        )
        if reached:
            print_timestamped(f"✓ Waypoint 1 reached! Altitude: {pos['altitude']:.2f}m")
        else:
            print_timestamped("✗ Failed to reach waypoint 1")
            
        sleep(3)  # Hover for 3 seconds
            
        # Waypoint 2: Climb to 10m
        print_timestamped("\n=== WAYPOINT 2: Climb to 10m ===")
        set_target_position(0, 0, -20.0)
        reached, pos = wait_for_position(
                connection, 0, 0, -20.0,
                tolerance_xy=1.0,
                tolerance_z=0.5,
                timeout=100
            )
        
        if reached:
            print_timestamped(f"✓ Waypoint 2 reached! Altitude: {pos['altitude']:.2f}m")
        else:
            print_timestamped("✗ Failed to reach waypoint 2")
            
        sleep(3)  # Hover for 3 seconds
            
        # Waypoint 3: Move to (10, 10, -10) - Northeast corner
        print_timestamped("\n=== WAYPOINT 3: Move to (10, 10, -10) ===")
        set_target_position(20, 20, -40.0)
        reached, pos = wait_for_position(
                connection, 20, 20, -40.0,
                tolerance_xy=1.5,  # Slightly larger tolerance for horizontal movement
                tolerance_z=0.5,
                timeout=124
        )
        if reached:
            print_timestamped(f"✓ Waypoint 3 reached! Pos: ({pos['x']:.2f}, {pos['y']:.2f}, {pos['altitude']:.2f}m)")
        else:
            print_timestamped("✗ Failed to reach waypoint 3")
            
        sleep(3)  # Hover for 3 seconds
            
        # Waypoint 4: Return to origin at 10m
        print_timestamped("\n=== WAYPOINT 4: Return to origin at 10m ===")
        set_target_position(0, 0, -20.0)
        reached, pos = wait_for_position(
                connection, 0, 0, -20.0,
                tolerance_xy=1.5,
                tolerance_z=0.5,
                timeout=120
            )
        if reached:
            print_timestamped("✓ Waypoint 4 reached! Back at origin")
        else:
            print_timestamped("✗ Failed to reach waypoint 4")
            
        sleep(3)  # Hover for 3 seconds
            
        # Waypoint 5: Land
        print_timestamped("\n=== WAYPOINT 5: Landing ===")
        set_target_position(0, 0, 0)
        reached, pos = wait_for_position(
                connection, 0, 0, 0,
                tolerance_xy=1.0,
                tolerance_z=0.3,  # Tighter tolerance for landing
                timeout=120
            )
        if reached:
            print_timestamped("✓ Landing complete!")
        else:
            print_timestamped("✗ Landing timeout")
            
        print_timestamped("\n=== MISSION COMPLETE ===")
            
            
    finally:
        stop_setpoint_thread()
        connection.close()
    
if __name__ == "__main__":
    main()