"""
Flight Controller Commands

Handles arming, mode changes, takeoff, landing, and OFFBOARD setpoint streaming.
"""

import threading
from time import time, sleep
from pymavlink import mavutil
from src.core.connection import print_timestamped
from src.core import constants as c


# Shared state for setpoint thread
target_position = {
    'x': 0.0,
    'y': 0.0,
    'z': 0.0
}

setpoint_thread_running = False
setpoint_thread = None


def send_setpoint_thread(connection, system_id, component_id):
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
        sleep(0.05)  # 50ms == 20Hz


def start_setpoint_thread(connection, system_id, component_id):
    """Start the background setpoint sender thread."""
    global setpoint_thread_running, setpoint_thread
    
    setpoint_thread_running = True
    setpoint_thread = threading.Thread(
        target=send_setpoint_thread,
        args=(connection, system_id, component_id),
        daemon=True
    )
    setpoint_thread.start()
    print_timestamped("Setpoint thread started at 20Hz")


def stop_setpoint_thread():
    """Stop the background setpoint sender thread."""
    global setpoint_thread_running, setpoint_thread
    
    setpoint_thread_running = False
    if setpoint_thread:
        setpoint_thread.join(timeout=2.0)
    print_timestamped("Setpoint thread stopped!")


def set_target_position(x, y, z):
    """
    Update the target position that the setpoint thread is sending.
    This is called from your main thread to command movement.
    
    NED coordinates:
    - x: North (positive = north, negative = south)
    - y: East (positive = east, negative = west)
    - z: Down (positive = down, NEGATIVE = up!)
    
    Args:
        x: North position (m)
        y: East position (m)
        z: Down position (m, negative for altitude)
    """
    global target_position
    target_position['x'] = x
    target_position['y'] = y
    target_position['z'] = z
    print_timestamped(f"Target updated: N={x}m, E={y}m, D={z}m")


def wait_for_setpoints_active(connection, timeout=30):
    """
    Wait until PX4 acknowledges receiving setpoints.
    This ensures OFFBOARD mode will work.
    
    Args:
        connection: MAVLink connection
        timeout: Maximum wait time (seconds)
    
    Returns:
        bool: True if setpoints acknowledged, False if timeout
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


def arm(connection, system_id, component_id, max_retries=5):
    """
    Arm the vehicle with retries.
    
    Args:
        connection: MAVLink connection
        system_id: Target system ID
        component_id: Target component ID
        max_retries: Number of arm attempts
    
    Returns:
        bool: True if armed successfully, False otherwise
    """
    for attempt in range(max_retries):
        print_timestamped(f"Arming attempt {attempt + 1}/{max_retries}...")
        
        connection.mav.command_long_send(
            system_id,
            component_id,
            400,  # MAV_CMD_COMPONENT_ARM_DISARM
            0,
            1,      # arm
            21196,  # force arm
            0, 0, 0, 0, 0
        )
        
        ack_msg = connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
        if not ack_msg:
            print_timestamped("✗ No ACK received")
            sleep(2)
            continue
        
        print_timestamped(f"  Result: {ack_msg.result}")
        
        if ack_msg.result == 0:
            print_timestamped("✓ Armed!")
            return True
        elif ack_msg.result == 1:  # TEMPORARILY_REJECTED
            print_timestamped("  ⚠ Temporarily rejected, retrying...")
            sleep(3)
            continue
        else:
            errors = {2: "DENIED", 3: "UNSUPPORTED", 4: "FAILED"}
            error_name = errors.get(ack_msg.result, f"UNKNOWN({ack_msg.result})")
            print_timestamped(f"✗ Arm FAILED: {error_name}")
            return False
    
    print_timestamped(f"✗ Failed to arm after {max_retries} attempts")
    return False


def set_mode(connection, system_id, component_id, mode_name):
    """
    Set flight mode.
    
    Args:
        connection: MAVLink connection
        system_id: Target system ID
        component_id: Target component ID
        mode_name: Mode name ('OFFBOARD') or mode number (6)
    
    Returns:
        bool: True if mode set successfully, False otherwise
    """
    print_timestamped(f'Setting flight mode to {mode_name}')
    
    if mode_name == 'OFFBOARD' or mode_name == 6:
        connection.mav.command_long_send(
            system_id,
            component_id,
            176,  # MAV_CMD_DO_SET_MODE
            0,
            1,  # custom mode
            6,  # OFFBOARD
            0, 0, 0, 0, 0
        )
    
    ack_msg = connection.recv_match(type=c.MSG_ACK, blocking=True, timeout=5)
    
    if not ack_msg:
        print_timestamped("No ACK received for mode change")
        return False
    
    if ack_msg.command == 176:
        if ack_msg.result == 0:
            print_timestamped(f'ACK: {ack_msg}')
            print_timestamped('Flight mode command accepted')
            
            # Wait longer and check multiple heartbeats
            sleep(2)
            
            # Check heartbeat multiple times (sometimes takes a moment)
            for attempt in range(3):
                heartbeat = connection.recv_match(type=c.MSG_HEARTBEAT, blocking=True, timeout=2)
                if heartbeat:
                    main_mode = (heartbeat.custom_mode >> 16) & 0xFF
                    print_timestamped(f"Attempt {attempt+1}: Mode = {main_mode}")
                    
                    if main_mode == 6:
                        print_timestamped("✓ Drone is now in OFFBOARD mode")
                        return True
                
                sleep(1)
            
            # If we get here, mode never changed
            print_timestamped("✗ Failed to enter OFFBOARD mode after 3 attempts")
            return False
        else:
            print_timestamped(f'Mode change rejected, result: {ack_msg.result}')
            return False
    
    return False


def takeoff(connection, system_id, component_id, height):
    """
    Command takeoff (used in non-OFFBOARD modes).
    
    Args:
        connection: MAVLink connection
        system_id: Target system ID
        component_id: Target component ID
        height: Takeoff altitude (meters)
    
    Returns:
        bool: True if command accepted, False otherwise
    """
    print_timestamped(f'Taking off to {height}m height')
    
    connection.mav.command_long_send(
        system_id,
        component_id,
        22,  # MAV_CMD_NAV_TAKEOFF
        0,
        0, 0, 0, 0,
        0, 0,
        height
    )
    
    ack_msg = connection.recv_match(type=c.MSG_ACK, blocking=True, timeout=5)
    
    if not ack_msg:
        print_timestamped("No ACK received for takeoff")
        return None
    
    if ack_msg.command == 22:
        if ack_msg.result == 0:
            print_timestamped(f'ACK: {ack_msg}')
            print_timestamped(f'Drone is climbing to {height} meters!')
            return True
        else:
            print_timestamped(f'Takeoff rejected, result: {ack_msg.result}')
            return False
    
    print_timestamped('Takeoff command failed!')
    return False


def land(connection, system_id, component_id):
    """
    Command landing.
    
    Args:
        connection: MAVLink connection
        system_id: Target system ID
        component_id: Target component ID
    
    Returns:
        bool: True if command accepted, False otherwise
    """
    print_timestamped("Landing...")
    
    connection.mav.command_long_send(
        system_id,
        component_id,
        21,  # MAV_CMD_NAV_LAND
        0,
        0, 0, 0, 0,
        0, 0, 0
    )
    
    ack_msg = connection.recv_match(type=c.MSG_ACK, blocking=True, timeout=5)
    
    if not ack_msg:
        print_timestamped("No ACK received for landing")
        return None
    
    if ack_msg.command == 21:
        if ack_msg.result == 0:
            print_timestamped(f'ACK: {ack_msg}')
            print_timestamped('Landing command accepted!')
            return True
        else:
            print_timestamped(f'Landing rejected, result: {ack_msg.result}')
            return False
    
    print_timestamped('Landing command failed!')
    return False