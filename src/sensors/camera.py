"""
Camera Control and Image Management

Handles camera triggering via MAVLink and image file management.
"""

import os
import shutil
from glob import glob
from datetime import datetime
from time import sleep
from src.core.connection import print_timestamped
from pymavlink import mavutil


def trigger_camera(connection, system_id, component_id, waypoint_num):
    """
    Trigger camera via MAVLink and copy image to project directory.
    
    Args:
        connection: MAVLink connection
        system_id: Target system ID
        component_id: Target component ID
        waypoint_num: Waypoint number for filename
    
    Note:
        Images are saved to: data/flights/images/
    """
    print_timestamped(f"  📸 Triggering camera at waypoint {waypoint_num}")
    
    # Send MAVLink camera trigger
    connection.mav.command_long_send(
        system_id,
        component_id,
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
    
    # Wait for camera to capture
    sleep(0.5)
    
    # Copy latest image from Gazebo to project
    try:
        # Gazebo saves to ~/.gz/gui/pictures
        gz_dir = os.path.expanduser("~/.gz/gui/pictures")
        
        # Get most recent image
        images = glob(f"{gz_dir}/*.png")
        if images:
            latest_image = max(images, key=os.path.getctime)
            
            # Create project images directory
            project_img_dir = "data/flights/images"
            os.makedirs(project_img_dir, exist_ok=True)
            
            # Copy with waypoint number in filename
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            dest_filename = f"waypoint_{waypoint_num:03d}_{timestamp}.png"
            dest_path = os.path.join(project_img_dir, dest_filename)
            
            shutil.copy2(latest_image, dest_path)
            print_timestamped(f"     ✓ Image saved: {dest_filename}")
            
    except Exception as e:
        print_timestamped(f"     ⚠ Image copy failed: {e}")


def cleanup_camera_images():
    """
    Clean up Gazebo's temporary image directory.
    """
    try:
        gz_dir = os.path.expanduser("~/.gz/gui/pictures")
        if os.path.exists(gz_dir):
            for file in glob(f"{gz_dir}/*.png"):
                os.remove(file)
            print_timestamped("✓ Cleaned up temporary camera images")
    except Exception as e:
        print_timestamped(f"⚠ Cleanup failed: {e}")