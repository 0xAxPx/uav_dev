#!/usr/bin/env python3
"""
Merge Roof Damage Datasets

Combines SmartRoof (8 classes) and Keyan (1 class) datasets.
Maps Keyan's generic 'damage' class to 'Mechanical Damage'.
"""

import os
import shutil
from pathlib import Path
import yaml

print("="*60)
print("MERGING ROOF DAMAGE DATASETS")
print("="*60)

# Configuration
SMARTROOF_DIR = "Roof-Damage-1"
KEYAN_DIR = "Roof-Damage-Keyan"
MERGED_DIR = "Roof-Damage-Merged"

# SmartRoof classes (0-7)
SMARTROOF_CLASSES = [
    'Blister',
    'Chipped Shingle',
    'Cracked Shingle',
    'Degranulation',
    'Dragons Tooth',
    'Hail Impact',
    'Mechanical Damage',
    'Puncture'
]

# Map Keyan's class 0 (damage) to SmartRoof class 6 (Mechanical Damage)
KEYAN_CLASS_MAPPING = {
    0: 6  # damage -> Mechanical Damage
}

def merge_dataset(split='train'):
    """Merge train/valid/test split."""
    print(f"\nMerging {split} split...")
    
    # Create directories
    merged_images = Path(MERGED_DIR) / split / 'images'
    merged_labels = Path(MERGED_DIR) / split / 'labels'
    merged_images.mkdir(parents=True, exist_ok=True)
    merged_labels.mkdir(parents=True, exist_ok=True)
    
    # Copy SmartRoof data (no modification needed - already 0-7)
    smartroof_images = Path(SMARTROOF_DIR) / split / 'images'
    smartroof_labels = Path(SMARTROOF_DIR) / split / 'labels'
    
    if smartroof_images.exists():
        for img_file in smartroof_images.iterdir():
            if img_file.suffix in ['.jpg', '.png', '.jpeg']:
                shutil.copy2(img_file, merged_images / img_file.name)
        
        for label_file in smartroof_labels.iterdir():
            if label_file.suffix == '.txt':
                shutil.copy2(label_file, merged_labels / label_file.name)
        
        smartroof_count = len(list(smartroof_images.glob('*.jpg'))) + \
                         len(list(smartroof_images.glob('*.png')))
        print(f"  ✓ SmartRoof: {smartroof_count} images")
    
    # Copy Keyan data (remap class 0 -> 6)
    keyan_images = Path(KEYAN_DIR) / split / 'images'
    keyan_labels = Path(KEYAN_DIR) / split / 'labels'
    
    if keyan_images.exists():
        for img_file in keyan_images.iterdir():
            if img_file.suffix in ['.jpg', '.png', '.jpeg']:
                # Rename to avoid conflicts
                new_name = f"keyan_{img_file.name}"
                shutil.copy2(img_file, merged_images / new_name)
        
        keyan_count = 0
        for label_file in keyan_labels.iterdir():
            if label_file.suffix == '.txt':
                new_name = f"keyan_{label_file.name}"
                
                # Remap class IDs
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                remapped_lines = []
                for line in lines:
                    parts = line.strip().split()
                    if parts:
                        old_class = int(parts[0])
                        new_class = KEYAN_CLASS_MAPPING.get(old_class, old_class)
                        parts[0] = str(new_class)
                        remapped_lines.append(' '.join(parts) + '\n')
                
                with open(merged_labels / new_name, 'w') as f:
                    f.writelines(remapped_lines)
                
                keyan_count += 1
        
        print(f"  ✓ Keyan: {keyan_count} images (remapped to Mechanical Damage)")

# Merge all splits
for split in ['train', 'valid', 'test']:
    merge_dataset(split)

# Create merged data.yaml
merged_config = {
    'path': '.',
    'train': 'train/images',
    'val': 'valid/images',
    'test': 'test/images',
    'nc': 8,
    'names': SMARTROOF_CLASSES
}

data_yaml_path = Path(MERGED_DIR) / 'data.yaml'
with open(data_yaml_path, 'w') as f:
    yaml.dump(merged_config, f, default_flow_style=False, sort_keys=False)

print("\n" + "="*60)
print("MERGE COMPLETE!")
print("="*60)

# Count final dataset
for split in ['train', 'valid', 'test']:
    merged_images = Path(MERGED_DIR) / split / 'images'
    if merged_images.exists():
        count = len(list(merged_images.glob('*.jpg'))) + \
                len(list(merged_images.glob('*.png')))
        print(f"{split.capitalize()}: {count} images")

print("\nClasses (8):")
for i, name in enumerate(SMARTROOF_CLASSES):
    print(f"  {i}: {name}")

print(f"\nMerged dataset location: {MERGED_DIR}/")
print(f"Configuration: {data_yaml_path}")
print("="*60)

print("\n✓ Ready to train with merged dataset!")
print(f"  Command: python3 src/vision/trainer.py --dataset {MERGED_DIR}")