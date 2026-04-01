#!/usr/bin/env python3
"""
Download Additional Roof Damage Datasets

Downloads multiple datasets from Roboflow Universe to increase training data.
"""

from roboflow import Roboflow
import os

print("="*60)
print("DOWNLOADING ADDITIONAL ROOF DAMAGE DATASETS")
print("="*60)

# Get API key
api_key = input("\nEnter your Roboflow API key: ").strip()

if not api_key:
    print("✗ No API key provided!")
    exit(1)

rf = Roboflow(api_key=api_key)

datasets_downloaded = []
total_images = 0

# Dataset 1: Keyan Roof Damage (127 images)
print("\n" + "-"*60)
print("1. Keyan Roof Damage Dataset (127 images)")
print("-"*60)
try:
    project = rf.workspace("keyan").project("roof-damage-detection")
    dataset1 = project.version(1).download("yolov8", location="Roof-Damage-Keyan")
    print(f"✓ Downloaded to: {dataset1.location}")
    datasets_downloaded.append(("Keyan", dataset1.location, 127))
    total_images += 127
except Exception as e:
    print(f"✗ Error: {e}")

# Dataset 2: Remote Roofing Hail Damage (99 images)
print("\n" + "-"*60)
print("2. Remote Roofing Hail Damage Dataset (99 images)")
print("-"*60)
try:
    project = rf.workspace("remote-roofing").project("hail-damage-batches")
    dataset2 = project.version(1).download("yolov8", location="Roof-Damage-Hail")
    print(f"✓ Downloaded to: {dataset2.location}")
    datasets_downloaded.append(("Hail", dataset2.location, 99))
    total_images += 99
except Exception as e:
    print(f"✗ Error: {e}")

# Summary
print("\n" + "="*60)
print("DOWNLOAD SUMMARY")
print("="*60)
print(f"Datasets downloaded: {len(datasets_downloaded)}")
print(f"Total new images: {total_images}")
print(f"Current dataset: 47 images")
print(f"Combined total: {total_images + 47} images")
print("\nDatasets:")
for name, location, count in datasets_downloaded:
    print(f"  - {name}: {location} ({count} images)")
print("="*60)

# Save locations for later
with open('downloaded_datasets.txt', 'w') as f:
    for name, location, count in datasets_downloaded:
        f.write(f"{name},{location},{count}\n")

print("\n✓ Dataset locations saved to: downloaded_datasets.txt")