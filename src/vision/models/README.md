# Trained Models

This directory contains trained YOLOv8 models for roof damage detection.

## Current Model

**roof_damage.pt** - Initial proof-of-concept model
- Dataset: Roboflow SmartRoof (47 images, 10 damage classes)
- Training: 100 epochs, YOLOv8 nano
- Metrics: mAP50=3.87%, Precision=23%, Recall=5%
- Size: ~6MB

## How to Get the Model

### Option 1: Train Your Own
```bash
python3 src/vision/trainer.py --dataset Roof-Damage-1 --epochs 100
```

### Option 2: Download Dataset & Train
```bash
# Download dataset
python3 src/vision/dowload.py

# Train model
python3 src/vision/trainer.py --dataset Roof-Damage-1
```

## Model Location

Trained models are saved to:
- `runs/detect/runs/train/roof_damage/weights/best.pt` (during training)
- `src/vision/models/roof_damage.pt` (final location)

**Note:** Models are git-ignored. Each developer trains their own or downloads from shared storage.
