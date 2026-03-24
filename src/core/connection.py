"""
MAVLink Connection Management

Handles connection to PX4 autopilot and basic utilities.
"""

from pymavlink import mavutil
from datetime import datetime
from src.core import constants as c


def print_timestamped(message):
    """Print message with timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}")


def connect_to_vehicle(connection_string):
    """
    Connect to vehicle and wait for heartbeat.
    
    Args:
        connection_string: MAVLink connection string (e.g., 'udp:127.0.0.1:14540')
    
    Returns:
        connection: MAVLink connection object
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


def preflight_checks(connection):
    """
    Run pre-flight checks (GPS fix, battery level).
    
    Args:
        connection: MAVLink connection
    
    Returns:
        bool: True if checks passed, False otherwise
    """
    # Check GPS
    gps_msg = connection.recv_match(type=c.MSG_GPS, blocking=True, timeout=2)
    if not gps_msg:
        print_timestamped("✗ No GPS data received")
        return None
    gps_fix_type = gps_msg.fix_type
    
    # Check battery
    sys_status_msg = connection.recv_match(type=c.MSG_SYS, blocking=True, timeout=3)
    if not sys_status_msg:
        print_timestamped("✗ No system status received")
        return None
    battery_remaining = sys_status_msg.battery_remaining
    
    # Verify GPS 3D fix and battery > 30%
    if gps_fix_type != 3:
        print_timestamped(f"✗ GPS fix type {gps_fix_type} (need 3D fix)")
        return False
    
    if battery_remaining <= 30:
        print_timestamped(f"✗ Battery too low: {battery_remaining}%")
        return False
    
    print_timestamped(
        f"✓ Pre-flight checks passed. Battery: {battery_remaining}%, GPS: 3D fix"
    )
    return True
