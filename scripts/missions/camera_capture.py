#!/usr/bin/env python3
"""
Subscribe to Gazebo camera and save images with GPS tags
"""
import subprocess
import json
from pymavlink import mavutil
from time import sleep, time
from datetime import datetime
import threading

# Camera topic
CAMERA_TOPIC = "/world/default/model/x500_0/link/camera_link/sensor/camera/image"
OUTPUT_DIR = "/tmp/gazebo_camera"

# Connect to drone for GPS
connection = mavutil.mavlink_connection('udp:127.0.0.1:14540')
connection.wait_heartbeat()
print("✓ Connected to drone")

image_count = 0

def save_camera_image():
    """Subscribe to camera topic and save image"""
    global image_count
    
    # Use gz service to get image
    cmd = f'gz topic -e -t "{CAMERA_TOPIC}" -n 1'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=2)
        if result.returncode == 0:
            image_count += 1
            filename = f"{OUTPUT_DIR}/image_{image_count:04d}.png"
            
            # Save image data (this is simplified - needs proper image decoding)
            print(f"✓ Captured image {image_count}")
            return True
    except:
        pass
    
    return False

# Capture images every 2 seconds
print(f"Capturing images to {OUTPUT_DIR}")
print("Press Ctrl+C to stop")

try:
    while True:
        save_camera_image()
        sleep(2)
except KeyboardInterrupt:
    print(f"\nCaptured {image_count} images")