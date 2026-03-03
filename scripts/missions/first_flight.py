from pymavlink import mavutil
from datetime import datetime
from time import sleep
from time import time

# Constants
CONNECTION_STRING = "udp:127.0.0.1:14550"
MSG_HEARTBEAT = "HEARTBEAT"
MSG_ACK = "COMMAND_ACK"
MSG_GPS = "GPS_RAW_INT"
MSG_SYS = "SYS_STATUS"
MSG_HUD = "VFR_HUD"


def print_timestamped(message):
    """Print message with timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}")
    
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
            print_timestamped(f'ACL {ack_msg}')
            print_timestamped("Armed!")
            return True
        else:
            print_timestamped(f'There is a problem with getting {MSG_ACK} for arming drone, result returned = {ack_msg.result}')
    else:
        print_timestamped('Arm failed!')
        return False

def set_mode(connection, system_id, component_id, mode):
    print_timestamped(f'Setting flight mode to {mode}')
    connection.mav.command_long_send(
        system_id,
        component_id,
        176,
        0,
        1, # MAV_MODE_FLAG_CUSTOM_MODE_ENABLED (1)
        mode, # X4_CUSTOM_MAIN_MODE_OFFBOARD (6)
        0,
        0,0,0,0
    )
    ack_msg = connection.recv_match(type=MSG_ACK, blocking=True, timeout = 5)
    if not ack_msg:
        return None
    if ack_msg and ack_msg.command == 176:
        if ack_msg.result == 0:
            print_timestamped(f'ACK:{ack_msg}')
            print_timestamped(f'Flight mode changed to {mode}!')
            heartbeat = connection.recv_match(type = MSG_HEARTBEAT, blocking = True, timeout = 2)
            if ((heartbeat.custom_mode >> 16) & 0xFF) == 6:
                print_timestamped("Drone is currently in Offboard mode")
            else:
                print_timestamped(f'Drone is in another mode. Main Mode ID: {(heartbeat.custom_mode >> 16) & 0xFF}')
            return True
        else:
            print_timestamped(f'There is a problem with getting {MSG_ACK} for setting mode as {mode}, result returned = {ack_msg.result}')
    else:
        print_timestamped('Setting of mode failed!')
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
        
    # send arm on
    if arm(connection, system_id, component_id):
        # mode == 6 (offboard)
        set_mode(connection, system_id, component_id, 6) 
        takeoff(connection,system_id, component_id, 5)
        if wait_for_altitude(connection, 5.0):
            print_timestamped("Hovering for 10 mins...")
            sleep(10)
            land(connection, system_id, component_id)
    else:
        print_timestamped('Drone was not armed!')
    
    
    connection.close()

if __name__ == "__main__":
    main()