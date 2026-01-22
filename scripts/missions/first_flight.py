from pymavlink import mavutil
from datetime import datetime
from time import sleep

# Constants
CONNECTION_STRING = "udp:127.0.0.1:14550"
MSG_HEARTBEAT = "HEARTBEAT"
MSG_ACK = "COMMAND_ACK"
MSG_GPS = "GPS_RAW_INT"
MSG_SYS = "SYS_STATUS"


def print_timestamped(message):
    """Print message with timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}")
    
def connect_to_vehicle(connection_string):
    """
    Connect to vehicle and wait for heartbeat.
    Returns connection object.
    """
    print(f"Connecting to vehicle on {connection_string}...")
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
        print(f'[{print_timestamped}] ACK:{ack_msg}')
        print(f'[{print_timestamped}] Armed!')
        return True
    else:
        print(f'[{print_timestamped}] Arm failed!')
        return False


def takeoff(connection, system_id, component_id, height):
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
        print(f'[{print_timestamped}] ACK:{ack_msg}')
        print(f'[{print_timestamped}] Drone is hovering at {height} meters!')
        return True
    else:
        print(f'[{print_timestamped}] Drone takeoff failed!')
        return False
    
    return

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
        print(f'[{print_timestamped}] ACK:{ack_msg}')
        print(f'[{print_timestamped}] Drone landed successfully!')
        return True
    else:
        print(f'[{print_timestamped}] Drone landing failed!')
        return False
    
    return

def wait_for_altitude(connection, target_alt, tolerance = 0.5):
    return
    


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
    if gps_fix_type != 3 and battery_remaining <=30:
        return False
    else:
        print(f'Pre-flight checks passed. Battery remain = {battery_remaining}, GPS fix type = {gps_fix_type}')
        
    # send arm on
    if arm(connection, system_id, component_id):
        takeoff(connection,system_id, component_id, 5)
        sleep(5)
        land(connection, system_id, component_id)
    else:
        print('Drone was not armed!')
    
    
    connection.close()

if __name__ == "__main__":
    main()