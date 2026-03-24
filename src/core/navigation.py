"""
Navigation and Position Management

Functions for getting position, calculating distances, and waiting for waypoints.
"""

import math
from time import time, sleep
from src.core.connection import print_timestamped
from src.core import constants as c


def get_current_position(connection, timeout=2):
    """
    Get drone's current position from LOCAL_POSITION_NED message.
    
    Args:
        connection: MAVLink connection object
        timeout: How long to wait for message (seconds)
    
    Returns:
        dict: {'x', 'y', 'z', 'vx', 'vy', 'vz', 'altitude', 'ground_speed', 'vertical_speed', 'timestamp'}
        None: If timeout or no message received
    """
    msg = connection.recv_match(type=c.MSG_LOC_POSIT_NED, blocking=True, timeout=timeout)
    
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


def get_current_altitude(connection, timeout=2):
    """Get current altitude in meters."""
    position = get_current_position(connection=connection, timeout=timeout)
    return position['altitude'] if position else None


def get_current_ground_speed(connection, timeout=2):
    """Get current horizontal speed in m/s."""
    position = get_current_position(connection=connection, timeout=timeout)
    return position['ground_speed'] if position else None


def get_current_vertical_speed(connection, timeout=2):
    """Get current vertical speed in m/s (positive = climbing)."""
    position = get_current_position(connection=connection, timeout=timeout)
    return position['vertical_speed'] if position else None


def get_position_xy(connection, timeout=2):
    """
    Get just horizontal position (useful for waypoint checks).
    
    Returns:
        tuple: (x, y) or None
    """
    pos = get_current_position(connection, timeout)
    return (pos['x'], pos['y']) if pos else None


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


def altitude_difference(pos1, pos2):
    """
    Calculate altitude difference (absolute value).
    Handles both 'altitude' and 'z' keys properly.
    
    Args:
        pos1: dict with 'altitude' or 'z' key
        pos2: dict with 'altitude' or 'z' key
    
    Returns:
        float: Altitude difference in meters
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
        tuple: (success: bool, final_position: dict)
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
        connection: MAVLink connection
        target_x, target_y, target_z: Target position
        tolerance_xy, tolerance_z: Position tolerances
        max_speed: Maximum ground speed to consider "stable" (m/s)
        stability_time: How long to remain stable (seconds)
        timeout, check_interval: Timing parameters
    
    Returns:
        tuple: (success: bool, final_position: dict)
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


def wait_for_altitude(connection, target_alt, tolerance=0.5, timeout=30):
    """
    Wait until altitude reaches target (legacy function).
    
    Args:
        connection: MAVLink connection
        target_alt: Target altitude in meters
        tolerance: Altitude tolerance in meters
        timeout: Maximum wait time
    
    Returns:
        bool: True if reached, False if timeout
    """
    start_time = time()
    
    while (time() - start_time) < timeout:
        msg = connection.recv_match(type=c.MSG_HUD, blocking=True, timeout=2)
        if msg:
            current_alt = msg.alt
            
            if abs(current_alt - target_alt) < tolerance:
                print_timestamped(f'Reached altitude {current_alt}m')
                return True
        sleep(0.1)
    
    print_timestamped("Timeout waiting for altitude")
    return False