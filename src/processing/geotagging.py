#!/usr/bin/env python3
"""
Geotag Images - Embed GPS EXIF data and convert to JPEG

Reads telemetry CSV and embeds GPS coordinates into image EXIF metadata.
Outputs JPEG files compatible with Google Earth and photogrammetry software.
"""

import pandas as pd
import piexif
from PIL import Image
import os
from glob import glob
from datetime import datetime


def decimal_to_dms(decimal_degrees):
    """
    Convert decimal degrees to degrees, minutes, seconds format for EXIF.
    
    Args:
        decimal_degrees: float (e.g., 47.1234)
    
    Returns:
        tuple: ((degrees, 1), (minutes, 1), (seconds, 100))
    """
    is_positive = decimal_degrees >= 0
    decimal_degrees = abs(decimal_degrees)
    
    degrees = int(decimal_degrees)
    minutes_decimal = (decimal_degrees - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    
    # EXIF format: (numerator, denominator)
    degrees_exif = (degrees, 1)
    minutes_exif = (minutes, 1)
    seconds_exif = (int(seconds * 100), 100)  # 2 decimal places
    
    return (degrees_exif, minutes_exif, seconds_exif)


def geotag_image(image_path, latitude, longitude, altitude):
    """
    Embed GPS coordinates into image EXIF data and convert to JPEG.
    
    Args:
        image_path: Path to PNG image
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees  
        altitude: Altitude in meters
    
    Returns:
        str: Path to geotagged JPEG file, or None if failed
    """
    try:
        # Load image
        img = Image.open(image_path)
        
        # Convert RGBA to RGB for JPEG (remove alpha channel)
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create EXIF dict
        exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}
        
        # Convert coordinates to DMS format
        lat_dms = decimal_to_dms(latitude)
        lon_dms = decimal_to_dms(longitude)
        
        # Determine hemisphere
        lat_ref = 'N' if latitude >= 0 else 'S'
        lon_ref = 'E' if longitude >= 0 else 'W'
        
        # Build GPS EXIF data
        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSLatitudeRef: lat_ref,
            piexif.GPSIFD.GPSLatitude: lat_dms,
            piexif.GPSIFD.GPSLongitudeRef: lon_ref,
            piexif.GPSIFD.GPSLongitude: lon_dms,
            piexif.GPSIFD.GPSAltitudeRef: 0,  # 0 = above sea level
            piexif.GPSIFD.GPSAltitude: (int(altitude * 100), 100),  # meters
        }
        
        exif_dict['GPS'] = gps_ifd
        
        # Convert to bytes
        exif_bytes = piexif.dump(exif_dict)
        
        # Create JPEG path
        jpeg_path = image_path.replace('.png', '.jpg')
        
        # Save as JPEG with GPS EXIF
        img.save(jpeg_path, 'JPEG', quality=95, exif=exif_bytes)
        
        return jpeg_path
        
    except Exception as e:
        print(f"Error geotagging {image_path}: {e}")
        return None


def extract_waypoint_gps(csv_path):
    """
    Extract GPS coordinates for each waypoint from telemetry CSV.
    
    Returns:
        dict: {waypoint_num: {'lat': lat, 'lon': lon, 'alt': alt, 'timestamp': ts}}
    """
    # Load telemetry
    df = pd.read_csv(csv_path)
    
    # Get unique waypoints
    waypoint_data = {}
    
    for waypoint_num in df['waypoint'].unique():
        # Get data for this waypoint
        wp_df = df[df['waypoint'] == waypoint_num]
        
        if len(wp_df) > 0:
            # Use first reading at waypoint (when arrived)
            first_row = wp_df.iloc[0]
            
            waypoint_data[int(waypoint_num)] = {
                'lat': first_row['lat'],
                'lon': first_row['lon'],
                'alt': first_row['altitude'],
                'timestamp': first_row['timestamp']
            }
    
    return waypoint_data


def geotag_flight_images(images_dir, csv_path, output_csv=None):
    """
    Geotag all images from a flight and convert to JPEG.
    
    Args:
        images_dir: Directory containing waypoint PNG images
        csv_path: Path to telemetry CSV
        output_csv: Optional path to save metadata CSV
    """
    print("="*60)
    print("GEOTAGGING FLIGHT IMAGES → JPEG")
    print("="*60)
    
    # Extract GPS data from telemetry
    print(f"\n[1/4] Reading telemetry: {csv_path}")
    waypoint_gps = extract_waypoint_gps(csv_path)
    print(f"✓ Found GPS data for {len(waypoint_gps)} waypoints")
    
    # Find all waypoint images
    print(f"\n[2/4] Scanning images: {images_dir}")
    image_files = sorted(glob(f"{images_dir}/waypoint_*.png"))
    print(f"✓ Found {len(image_files)} PNG images")
    
    # Geotag each image
    print(f"\n[3/4] Converting to JPEG with GPS EXIF...")
    
    metadata = []
    success_count = 0
    
    for image_path in image_files:
        # Extract waypoint number from filename
        # Format: waypoint_001_2026-03-23_19-40-00.png
        filename = os.path.basename(image_path)
        waypoint_num = int(filename.split('_')[1])
        
        # Get GPS for this waypoint
        if waypoint_num in waypoint_gps:
            gps = waypoint_gps[waypoint_num]
            
            # Geotag image and convert to JPEG
            jpeg_path = geotag_image(
                image_path,
                gps['lat'],
                gps['lon'],
                gps['alt']
            )
            
            if jpeg_path:
                jpeg_filename = os.path.basename(jpeg_path)
                print(f"  ✓ {jpeg_filename}: ({gps['lat']:.6f}, {gps['lon']:.6f}, {gps['alt']:.1f}m)")
                success_count += 1
                
                metadata.append({
                    'waypoint': waypoint_num,
                    'filename': jpeg_filename,
                    'latitude': gps['lat'],
                    'longitude': gps['lon'],
                    'altitude': gps['alt'],
                    'timestamp': gps['timestamp']
                })
            else:
                print(f"  ✗ {filename}: FAILED")
        else:
            print(f"  ⚠ {filename}: No GPS data for waypoint {waypoint_num}")
    
    # Save metadata CSV
    if output_csv and metadata:
        print(f"\n[4/4] Saving metadata: {output_csv}")
        metadata_df = pd.DataFrame(metadata)
        metadata_df.to_csv(output_csv, index=False)
        print(f"✓ Metadata saved")
    
    # Summary
    print("\n" + "="*60)
    print("GEOTAGGING COMPLETE")
    print("="*60)
    print(f"Total PNG Images: {len(image_files)}")
    print(f"Successfully Geotagged JPEGs: {success_count}")
    print(f"Failed: {len(image_files) - success_count}")
    if output_csv:
        print(f"Metadata CSV: {output_csv}")
    print("\n📍 GOOGLE EARTH IMPORT:")
    print(f"   1. Open Google Earth")
    print(f"   2. File → Import")
    print(f"   3. Select all waypoint_*.jpg from {images_dir}/")
    print(f"   4. Images will appear at GPS locations!")
    print("="*60)
    
    return metadata


def verify_geotag(image_path):
    """
    Verify GPS EXIF data in an image.
    
    Args:
        image_path: Path to image
    """
    try:
        img = Image.open(image_path)
        exif_dict = piexif.load(img.info.get('exif', b''))
        
        if 'GPS' in exif_dict and exif_dict['GPS']:
            gps = exif_dict['GPS']
            
            # Extract coordinates
            lat = gps.get(piexif.GPSIFD.GPSLatitude)
            lon = gps.get(piexif.GPSIFD.GPSLongitude)
            alt = gps.get(piexif.GPSIFD.GPSAltitude)
            
            if lat and lon:
                print(f"\n✓ GPS EXIF found in {os.path.basename(image_path)}")
                print(f"  Latitude: {lat}")
                print(f"  Longitude: {lon}")
                if alt:
                    print(f"  Altitude: {alt[0]/alt[1]:.1f}m")
                return True
        
        print(f"✗ No GPS EXIF in {os.path.basename(image_path)}")
        return False
        
    except Exception as e:
        print(f"Error reading EXIF: {e}")
        return False


if __name__ == "__main__":
    # Paths
    IMAGES_DIR = "images"
    TELEMETRY_CSV = "logs/flight_efficient_2026-03-23_19-18-50.csv"
    METADATA_CSV = "images/image_metadata.csv"
    
    # Geotag all images
    metadata = geotag_flight_images(
        images_dir=IMAGES_DIR,
        csv_path=TELEMETRY_CSV,
        output_csv=METADATA_CSV
    )
    
    # Verify first JPEG
    if metadata:
        first_jpeg = os.path.join(IMAGES_DIR, metadata[0]['filename'])
        if os.path.exists(first_jpeg):
            print("\n" + "="*60)
            print("VERIFICATION TEST")
            print("="*60)
            verify_geotag(first_jpeg)