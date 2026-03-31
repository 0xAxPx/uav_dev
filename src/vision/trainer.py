"""
YOLOv8 Trainer for Roof Damage Detection

Trains a YOLOv8 model on the Roof Damage dataset.
"""

import os
from pathlib import Path
from ultralytics import YOLO
import yaml


class RoofDamageTrainer:
    """
    Trainer for YOLOv8 roof damage detection model.
    """
    
    def __init__(self, dataset_path: str, model_size: str = 'n'):
        """
        Initialize trainer.
        
        Args:
            dataset_path: Path to dataset root (contains data.yaml)
            model_size: YOLOv8 model size:
                - 'n' (nano) - fastest, smallest, lowest accuracy
                - 's' (small) - good balance
                - 'm' (medium) - better accuracy
                - 'l' (large) - high accuracy, slower
                - 'x' (xlarge) - best accuracy, slowest
        """
        self.dataset_path = Path(dataset_path)
        self.model_size = model_size
        
        # Verify dataset exists
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")
        
        # Check for data.yaml
        self.data_yaml = self.dataset_path / 'data.yaml'
        if not self.data_yaml.exists():
            raise FileNotFoundError(f"data.yaml not found at {self.data_yaml}")
        
        # Load dataset config
        with open(self.data_yaml, 'r') as f:
            self.dataset_config = yaml.safe_load(f)
        
        print(f"Dataset: {self.dataset_path}")
        print(f"Classes: {self.dataset_config['nc']}")
        print(f"Names: {self.dataset_config['names']}")
    
    def train(self, 
              epochs: int = 100,
              imgsz: int = 640,
              batch: int = 16,
              patience: int = 50,
              save_dir: str = 'runs/train',
              device: str = 'mps',
              **kwargs):
        """
        Train YOLOv8 model.
        
        Args:
            epochs: Number of training epochs (default: 100)
            imgsz: Image size (default: 640)
            batch: Batch size (default: 16, reduce if OOM)
            patience: Early stopping patience (default: 50)
            save_dir: Directory to save results
            device: Device to train on ('mps' for Mac, 'cuda' for GPU, 'cpu')
            **kwargs: Additional YOLO training arguments
        """
        # Initialize YOLOv8 model
        model_name = f'yolov8{self.model_size}.pt'
        print(f"\nInitializing YOLOv8{self.model_size.upper()} model...")
        print(f"Pre-trained weights: {model_name}")
        
        model = YOLO(model_name)
        
        # Train model
        print("\n" + "="*60)
        print("STARTING TRAINING")
        print("="*60)
        print(f"Epochs: {epochs}")
        print(f"Image size: {imgsz}")
        print(f"Batch size: {batch}")
        print(f"Device: {device}")
        print(f"Patience: {patience}")
        print("="*60 + "\n")
        
        results = model.train(
            data=str(self.data_yaml),
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            patience=patience,
            save=True,
            project=save_dir,
            name='roof_damage',
            device=device,
            verbose=True,
            **kwargs
        )
        
        print("\n" + "="*60)
        print("✓ TRAINING COMPLETE!")
        print("="*60)
        
        # Get best model path
        best_model = Path(save_dir) / 'roof_damage' / 'weights' / 'best.pt'
        print(f"Best model saved to: {best_model}")
        
        return results, str(best_model)
    
    def validate(self, model_path: str, **kwargs):
        """
        Validate trained model.
        
        Args:
            model_path: Path to trained model (.pt file)
            **kwargs: Additional YOLO validation arguments
        """
        print(f"\nValidating model: {model_path}")
        
        model = YOLO(model_path)
        results = model.val(data=str(self.data_yaml), **kwargs)
        
        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60)
        print(f"mAP50: {results.box.map50:.3f}")
        print(f"mAP50-95: {results.box.map:.3f}")
        print(f"Precision: {results.box.mp:.3f}")
        print(f"Recall: {results.box.mr:.3f}")
        print("="*60)
        
        return results
    
    def export_model(self, model_path: str, export_format: str = 'onnx'):
        """
        Export model to different format.
        
        Args:
            model_path: Path to trained model
            export_format: Export format ('onnx', 'torchscript', 'coreml', etc.)
        """
        print(f"\nExporting model to {export_format}...")
        
        model = YOLO(model_path)
        model.export(format=export_format)
        
        print("✓ Model exported!")


def main():
    """
    Example training script.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Train YOLOv8 for roof damage detection')
    parser.add_argument('--dataset', type=str, default='Roof-Damage-1',
                        help='Path to dataset directory')
    parser.add_argument('--model', type=str, default='n',
                        choices=['n', 's', 'm', 'l', 'x'],
                        help='Model size (n=nano, s=small, m=medium, l=large, x=xlarge)')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of training epochs')
    parser.add_argument('--batch', type=int, default=16,
                        help='Batch size')
    parser.add_argument('--imgsz', type=int, default=640,
                        help='Image size')
    parser.add_argument('--device', type=str, default='mps',
                        help='Training device (mps/cuda/cpu)')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = RoofDamageTrainer(
        dataset_path=args.dataset,
        model_size=args.model
    )
    
    # Train model
    _, best_model_path = trainer.train(
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device
    )
    
    # Validate model
    trainer.validate(best_model_path)
    
    # Move best model to src/vision/models/
    import shutil
    os.makedirs('src/vision/models', exist_ok=True)
    final_path = 'src/vision/models/roof_damage.pt'
    shutil.copy(best_model_path, final_path)
    print(f"\n✓ Model copied to: {final_path}")


if __name__ == "__main__":
    main()