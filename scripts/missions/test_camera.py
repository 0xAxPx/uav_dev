from pymavlink import mavutil
from time import sleep

# Connect to drone
connection = mavutil.mavlink_connection('udp:127.0.0.1:14540')
connection.wait_heartbeat()
print("✓ Connected!")

# Trigger camera 5 times
for i in range(5):
    print(f"Triggering camera {i+1}/5...")
    
    connection.mav.command_long_send(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL,
        0,  # confirmation
        0,  # session control
        0,  # zoom position
        0,  # zoom step
        0,  # focus lock
        1,  # shooting command (1 = take photo)
        0,  # command identity
        0   # extra param
    )
    sleep(2)

print("\nCheck /tmp/gazebo_camera/ for images!")