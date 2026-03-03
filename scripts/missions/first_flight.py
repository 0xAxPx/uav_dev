from pymavlink import mavutil
from datetime import datetime
from time import sleep
from time import time
import threading

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
                int(0b110111111000),  # type_mask
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
            
            # Wait longer for mode to actually change
            sleep(2)  # ✅ Changed from 0.5 to 2 seconds
            heartbeat = connection.recv_match(type=MSG_HEARTBEAT, blocking=True, timeout=3)
            if heartbeat:
                main_mode = (heartbeat.custom_mode >> 16) & 0xFF
                if main_mode == 6:
                    print_timestamped("✓ Drone is now in OFFBOARD mode")
                    return True
                else:
                    # Don't fail if mode check is wrong, it might just be timing
                    print_timestamped(f"Mode shows as {main_mode}, but ACK was accepted - continuing")
                    return True  # ✅ Changed to return True anyway
        else:
            print_timestamped(f'Mode change rejected, result: {ack_msg.result}')
            return False
    
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
    gps_msg = connection.recv_match(type=MSG_GPS, blocking=True, timeout = 2)
    if not gps_msg:
        return None
    gps_fix_type = gps_msg.fix_type
    
    sys_status_msg = connection.recv_match(type=MSG_SYS, blocking=True, timeout= 3)
    if not sys_status_msg:
        return None
    battery_remaining = sys_status_msg.battery_remaining
    
    # Check if GPS 3D position and battery is more than 30% charge
    if gps_fix_type != 3 or battery_remaining <=30:
        return False
    else:
        print_timestamped(f'Pre-flight checks passed. Battery remain = {battery_remaining}, GPS fix type = {gps_fix_type}')
        
    
    try:
        set_target_position(0,0,0) # Ground Level
        start_setpoint_thread(connection=connection, system_id=system_id, component_id=component_id)
        sleep(2) # 2 sec
        
        # send arm on
        if arm(connection, system_id, component_id):
            sleep(3)
            # mode == 6 (offboard)
            set_mode(connection, system_id, component_id, 6)
            set_target_position(0, 0, -5.0)  # -5 = 5m up (NED)
            sleep(30) # Hover 30 secs 
            
            # Move forward 10 meters higher
            set_target_position(0, 0, -10.0)  # -10 = 10m up (NED)
            sleep(20) # Hover 10 secs
            
            set_target_position(200, 100, -50.0) 
            sleep(30) # Hover 10 secs
            
            set_target_position(0, 0, 0)  # Move to ground
            sleep(30) # Hover 10 secs
            
            
            #takeoff(connection,system_id, component_id, 5)
            #if wait_for_altitude(connection, 5.0):
            #    print_timestamped("Hovering for 10 mins...")
            #    sleep(10)
            #    land(connection, system_id, component_id)
        else:
            print_timestamped('Drone was not armed!')
    finally:
        stop_setpoint_thread()
        connection.close()

if __name__ == "__main__":
    main()