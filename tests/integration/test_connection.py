"""
MAVLink Telemetry Reader
Connects to PX4 SITL and reads basic telemetry data.
"""

from pymavlink import mavutil
from datetime import datetime
from math import pi
from time import sleep

# Constants
CONNECTION_STRING = "udp:127.0.0.1:14550"
GPS_COORDINATE_SCALE = 1e7
MILLIVOLT_TO_VOLT = 1000
MILLIMETER_TO_METER = 1000

# Message types
MSG_HEARTBEAT = "HEARTBEAT"
MSG_GPS = "GPS_RAW_INT"
MSG_BATTERY = "SYS_STATUS"
MSG_VFR_HUD = "VFR_HUD"
MSG_ATTITUDE = "ATTITUDE"


def rad_to_deg(radians):
    """Convert radians to degrees."""
    return radians * (180 / pi)


def print_timestamped(message):
    """Print message with timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}")


def read_message(connection, msg_type, timeout=4):
    """
    Read a specific message type from MAVLink connection.
    Returns None if message not received.
    """
    msg = connection.recv_match(type=msg_type, blocking=True, timeout=timeout)
    return msg


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


def read_gps(connection):
    """Read and return GPS data."""
    msg = read_message(connection, MSG_GPS)
    if not msg:
        return None
    
    return {
        'lat': msg.lat / GPS_COORDINATE_SCALE,
        'lon': msg.lon / GPS_COORDINATE_SCALE,
        'alt': msg.alt / MILLIMETER_TO_METER,
        'satellites': msg.satellites_visible,
        'fix_type': msg.fix_type
    }


def read_battery(connection):
    """Read and return battery data."""
    msg = read_message(connection, MSG_BATTERY)
    if not msg:
        return None
    
    return {
        'voltage': msg.voltage_battery / MILLIVOLT_TO_VOLT,
        'current': msg.current_battery / 100.0,  # centi-amps to amps
        'remaining': msg.battery_remaining
    }


def read_vfr_hud(connection):
    """Read and return VFR HUD data."""
    msg = read_message(connection, MSG_VFR_HUD)
    if not msg:
        return None
    
    return {
        'altitude': msg.alt,
        'groundspeed': msg.groundspeed,
        'heading': msg.heading,
        'throttle': msg.throttle,
        'climb_rate': msg.climb
    }


def read_attitude(connection):
    """Read and return attitude data in degrees."""
    msg = read_message(connection, MSG_ATTITUDE)
    if not msg:
        return None
    
    return {
        'roll': rad_to_deg(msg.roll),
        'pitch': rad_to_deg(msg.pitch),
        'yaw': rad_to_deg(msg.yaw)
    }


def read_all_telemetry(connection):
    """
    Read all telemetry data and return as dictionary.
    Returns None if any critical message fails.
    """
    # Read heartbeat first
    heartbeat = read_message(connection, MSG_HEARTBEAT)
    if not heartbeat:
        print("ERROR: No heartbeat received")
        return None
    
    # Read all telemetry
    gps = read_gps(connection)
    battery = read_battery(connection)
    vfr = read_vfr_hud(connection)
    attitude = read_attitude(connection)
    
    # Check if all data received
    if not all([gps, battery, vfr, attitude]):
        print("WARNING: Some telemetry data missing")
        return None
    
    return {
        'gps': gps,
        'battery': battery,
        'vfr': vfr,
        'attitude': attitude,
        'flight_mode': connection.flightmode
    }


def print_telemetry(telemetry):
    """Print telemetry data in readable format."""
    if not telemetry:
        print("No telemetry data to display")
        return
    
    print("\n" + "="*50)
    print_timestamped("TELEMETRY DATA")
    print("="*50)
    
    # GPS
    gps = telemetry['gps']
    print_timestamped(
        f"GPS: {gps['lat']:.6f}°N, {gps['lon']:.6f}°E, "
        f"Alt: {gps['alt']:.2f}m ({gps['satellites']} sats)"
    )
    
    # Battery
    bat = telemetry['battery']
    print_timestamped(
        f"Battery: {bat['voltage']:.2f}V, "
        f"{bat['current']:.2f}A, "
        f"{bat['remaining']}% remaining"
    )
    
    # VFR HUD
    vfr = telemetry['vfr']
    print_timestamped(
        f"Altitude: {vfr['altitude']:.2f}m, "
        f"Speed: {vfr['groundspeed']:.2f}m/s, "
        f"Heading: {vfr['heading']}°"
    )
    
    # Attitude
    att = telemetry['attitude']
    print_timestamped(
        f"Attitude: Roll={att['roll']:.2f}°, "
        f"Pitch={att['pitch']:.2f}°, "
        f"Yaw={att['yaw']:.2f}°"
    )
    
    # Flight mode
    print_timestamped(f"Flight Mode: {telemetry['flight_mode']}")
    print("="*50 + "\n")


def main():
    """Main function."""
    connection = None
    
    try:
        # Connect to vehicle
        connection = connect_to_vehicle(CONNECTION_STRING)
        
        # Read telemetry once
        print("\nReading telemetry...")
        telemetry = read_all_telemetry(connection)
        
        # Print results
        print_telemetry(telemetry)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        # Clean up
        if connection:
            connection.close()
            print("Connection closed")


if __name__ == "__main__":
    main()