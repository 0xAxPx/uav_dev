"""
Roof Damage Detector

YOLOv8-based detector for identifying roof damage in drone inspection images.
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
from ultralytics import YOLO
from PIL import Image


class RoofDamageDetector:
    """
    YOLOv8-based detector for roof damage.
    
    Classes:
        0: crack - Roof surface cracks/fractures
        1: missing_tile - Missing or displaced tiles
        2: water_damage - Water stains/pooling
        3: debris - Leaves, branches, trash
    """
    
    # Class definitions (auto-loaded from model)
    CLASS_NAMES = None  # Will be set from model.names in __init__
    
    # Severity thresholds (based on area in pixels)
    SEVERITY_THRESHOLDS = {
        'minor': 1000,      # < 1000 px²
        'moderate': 5000,   # 1000-5000 px²
        'critical': 5000    # > 5000 px²
    }
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.5):
        """
        Initialize detector.
        
        Args:
            model_path: Path to trained YOLOv8 model (.pt file)
            confidence_threshold: Minimum confidence to accept detection (0-1)
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "You need to train a model first or download pre-trained weights."
            )
        
        # Load YOLOv8 model
        print(f"Loading model from {model_path}...")
        self.model = YOLO(model_path)
        
        # Auto-load class names from model
        self.CLASS_NAMES = self.model.names
        
        print(f"✓ Model loaded successfully!")
        print(f"  Confidence threshold: {confidence_threshold}")
        print(f"  Classes ({len(self.CLASS_NAMES)}): {list(self.CLASS_NAMES.values())}")
    
    def detect(self, image_path: str, save_annotated: bool = False) -> List[Dict]:
        """
        Run detection on a single image.
        
        Args:
            image_path: Path to image file
            save_annotated: If True, save image with bounding boxes
        
        Returns:
            List of detections, each containing:
                - class_id: int
                - class_name: str
                - confidence: float
                - bbox: [x1, y1, x2, y2]
                - area: float (pixels²)
                - severity: str (minor/moderate/critical)
        """
        # Run inference
        results = self.model.predict(
            image_path,
            conf=self.confidence_threshold,
            verbose=False
        )
        
        detections = []
        
        # Parse results
        for result in results:
            boxes = result.boxes
            
            if boxes is None or len(boxes) == 0:
                continue
            
            for box in boxes:
                # Extract detection data
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                
                # Calculate area
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                area = width * height
                
                # Determine severity based on area
                if area < self.SEVERITY_THRESHOLDS['minor']:
                    severity = 'minor'
                elif area < self.SEVERITY_THRESHOLDS['moderate']:
                    severity = 'moderate'
                else:
                    severity = 'critical'
                
                detection = {
                    'class_id': class_id,
                    'class_name': self.CLASS_NAMES.get(class_id, 'unknown'),
                    'confidence': confidence,
                    'bbox': bbox,
                    'area': area,
                    'severity': severity
                }
                
                detections.append(detection)
        
        # Save annotated image if requested
        if save_annotated and len(detections) > 0:
            annotated_path = image_path.replace('.jpg', '_annotated.jpg')
            annotated_path = annotated_path.replace('.png', '_annotated.png')
            
            # YOLOv8 provides annotated image
            annotated_img = results[0].plot()  # Returns numpy array
            Image.fromarray(annotated_img).save(annotated_path)
        
        return detections
    
    def detect_batch(self, images_dir: str, pattern: str = "*.jpg") -> Dict[str, List[Dict]]:
        """
        Run detection on all images in a directory.
        
        Args:
            images_dir: Directory containing images
            pattern: File pattern to match (e.g., "*.jpg", "waypoint_*.png")
        
        Returns:
            Dictionary mapping image filename to list of detections
        """
        images_path = Path(images_dir)
        image_files = sorted(images_path.glob(pattern))
        
        if not image_files:
            print(f"⚠ No images found in {images_dir} matching {pattern}")
            return {}
        
        print(f"\nRunning detection on {len(image_files)} images...")
        print(f"Directory: {images_dir}")
        print(f"Pattern: {pattern}\n")
        
        all_detections = {}
        
        for i, image_file in enumerate(image_files, 1):
            image_name = image_file.name
            print(f"[{i}/{len(image_files)}] Processing {image_name}...", end=' ')
            
            detections = self.detect(str(image_file))
            all_detections[image_name] = detections
            
            print(f"✓ {len(detections)} detections")
        
        print(f"\n✓ Batch detection complete!")
        return all_detections
    
    def save_results(self, detections: Dict[str, List[Dict]], output_dir: str):
        """
        Save detection results to CSV and generate summary.
        
        Args:
            detections: Dictionary from detect_batch()
            output_dir: Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Flatten detections into rows for CSV
        rows = []
        for image_name, image_detections in detections.items():
            for det in image_detections:
                row = {
                    'image': image_name,
                    'class_id': det['class_id'],
                    'class_name': det['class_name'],
                    'confidence': det['confidence'],
                    'x1': det['bbox'][0],
                    'y1': det['bbox'][1],
                    'x2': det['bbox'][2],
                    'y2': det['bbox'][3],
                    'area_px': det['area'],
                    'severity': det['severity']
                }
                rows.append(row)
        
        if not rows:
            print("⚠ No detections to save")
            return
        
        # Save to CSV
        df = pd.DataFrame(rows)
        csv_path = os.path.join(output_dir, 'detections.csv')
        df.to_csv(csv_path, index=False)
        print(f"✓ Detections saved to: {csv_path}")
        
        # Generate summary statistics
        summary = {
            'total_images': len(detections),
            'total_detections': len(rows),
            'detections_by_class': df['class_name'].value_counts().to_dict(),
            'detections_by_severity': df['severity'].value_counts().to_dict(),
            'average_confidence': df['confidence'].mean()
        }
        
        # Print summary
        print("\n" + "="*60)
        print("DETECTION SUMMARY")
        print("="*60)
        print(f"Total Images: {summary['total_images']}")
        print(f"Total Detections: {summary['total_detections']}")
        print(f"\nBy Class:")
        for class_name, count in summary['detections_by_class'].items():
            print(f"  {class_name}: {count}")
        print(f"\nBy Severity:")
        for severity, count in summary['detections_by_severity'].items():
            print(f"  {severity}: {count}")
        print(f"\nAverage Confidence: {summary['average_confidence']:.2%}")
        print("="*60)
        
        # Save summary to JSON
        import json
        summary_path = os.path.join(output_dir, 'summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Summary saved to: {summary_path}")
    
    def get_severity_color(self, severity: str) -> Tuple[int, int, int]:
        """Get BGR color for severity level (for drawing boxes)."""
        colors = {
            'minor': (0, 255, 0),      # Green
            'moderate': (0, 165, 255),  # Orange
            'critical': (0, 0, 255)     # Red
        }
        return colors.get(severity, (255, 255, 255))


# Example usage
if __name__ == "__main__":
    import sys
    
    # Demo: Show how to use the detector
    print("="*60)
    print("ROOF DAMAGE DETECTOR - DEMO")
    print("="*60)
    
    model_path = "src/vision/models/roof_damage.pt"
    
    if not os.path.exists(model_path):
        print(f"\n⚠ Model not found at {model_path}")
        print("\nTo use this detector, you need a trained model.")
        print("Options:")
        print("  1. Train your own model (see src/vision/trainer.py)")
        print("  2. Download pre-trained weights")
        print("  3. Use base YOLOv8 model for testing (yolov8n.pt)")
        sys.exit(1)
    
    # Initialize detector
    detector = RoofDamageDetector(model_path, confidence_threshold=0.5)
    
    # Run detection on flight images
    images_dir = "data/flights/images"
    if os.path.exists(images_dir):
        detections = detector.detect_batch(images_dir, pattern="waypoint_*.jpg")
        detector.save_results(detections, output_dir="data/outputs/detections")
    else:
        print(f"\n⚠ Images directory not found: {images_dir}")