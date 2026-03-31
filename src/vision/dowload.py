#!/usr/bin/env python3
"""
Download Roof Damage Dataset from Roboflow

Downloads and prepares training dataset for YOLOv8.
"""

from roboflow import Roboflow
import os

# Initialize Roboflow
print("="*60)
print("DOWNLOADING ROOF DAMAGE DATASET")
print("="*60)

# You'll need to create a free account at https://roboflow.com
# and get your API key from https://app.roboflow.com/settings/api

print("\nTo download the dataset, you need a Roboflow API key.")
print("1. Go to https://roboflow.com and create a free account")
print("2. Get your API key from https://app.roboflow.com/settings/api")
print("3. Enter it below:\n")

api_key = input("Enter your Roboflow API key: ").strip()

if not api_key:
    print("\n✗ No API key provided. Exiting...")
    exit(1)

# Initialize Roboflow with API key
rf = Roboflow(api_key=api_key)

# Download the Roof Damage dataset
print("\nDownloading 'Roof Damage' dataset...")
print("Project: smartroof/roof-damage-ukqfw")

try:
    project = rf.workspace("smartroof").project("roof-damage-ukqfw")
    dataset = project.version(1).download("yolov8")
    
    print("\n" + "="*60)
    print("✓ DATASET DOWNLOADED SUCCESSFULLY!")
    print("="*60)
    print(f"Location: {dataset.location}")
    print(f"\nDataset structure:")
    print(f"  {dataset.location}/train/  - Training images + labels")
    print(f"  {dataset.location}/valid/  - Validation images + labels")
    print(f"  {dataset.location}/test/   - Test images + labels")
    print(f"  {dataset.location}/data.yaml - Dataset config")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ Error downloading dataset: {e}")
    print("\nAlternative: Download manually from:")
    print("https://universe.roboflow.com/smartroof/roof-damage-ukqfw/dataset/1")
    exit(1)