# Training Progress Log

## Milestone 1 - April 29, 2026

### Dataset
- **Before:** 110 images (Roof-Damage-Merged)
- **Added:** 41 new labeled images (UK roofs)
- **After:** 124 images (Roof-Damage-v2-151imgs)

### Model Performance
- **Baseline (roof_damage9):** 6.14% mAP
- **New (roof_v2_124imgs2):** 20.77% mAP
- **Improvement:** +14.63% (3.4x better!)

### Performance by Class
| Class | mAP50 | Images | Notes |
|-------|-------|--------|-------|
| Moss Growth | 39.1% | 47 | Best performing ✅ |
| Cracked Flashing | 36.7% | 100 | Second best ✅ |
| Missing Shingle | 28.5% | 4 | Good |
| Chipped Shingle | 20.4% | 23 | Acceptable |
| Damaged Shingle | 12.4% | 22 | Needs more data |
| Debris | 7.48% | 15 | Needs more data |
| Hail Impact | 0.86% | 17 | Needs more data |

### Training Details
- **Duration:** 13.1 hours (100 epochs)
- **Hardware:** Apple M3 Pro (CPU)
- **Model:** YOLOv8n
- **Best weights:** runs/detect/roof_v2_124imgs2/weights/best.pt

### Next Steps
1. ✅ Model updated and tested
2. 📸 First real drone flight practice
3. 🎯 Collect 400+ images from first 5 inspections
4. 🚀 Target: 30-35% mAP with 500+ images

### Files Updated
- `models/best.pt` → roof_v3_124imgs_20.77mAP.pt
- `Roof-Damage-v2-151imgs/` → New merged dataset
- Training results: `runs/detect/roof_v2_124imgs2/`
