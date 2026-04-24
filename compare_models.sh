#!/bin/bash

echo "🏆 MODEL COMPARISON"
echo "==================="
echo ""

best_map=0
best_model=""

for model_dir in ./runs/detect/runs/train/roof_damage*; do
    if [ -f "$model_dir/results.csv" ]; then
        model_name=$(basename "$model_dir")
        
        # Get mAP50 from last line of results.csv (column 8 or 9)
        # Try different column positions
        map50=$(tail -1 "$model_dir/results.csv" | awk -F',' '{print $8}' | tr -d ' ')
        
        if [ -z "$map50" ] || [ "$map50" = "metrics/mAP50(B)" ]; then
            map50=$(tail -1 "$model_dir/results.csv" | awk -F',' '{print $9}' | tr -d ' ')
        fi
        
        epochs=$(wc -l < "$model_dir/results.csv" | tr -d ' ')
        size=$(du -sh "$model_dir" | cut -f1)
        
        echo "📦 $model_name"
        echo "   Epochs: $((epochs - 1))"
        echo "   mAP50: $map50"
        echo "   Size: $size"
        echo "   Path: $model_dir/weights/best.pt"
        echo ""
        
        # Track best model (crude comparison)
        if [ ! -z "$map50" ] && [ "$map50" != "metrics/mAP50(B)" ]; then
            current_int=$(echo "$map50 * 10000" | bc 2>/dev/null | cut -d'.' -f1)
            best_int=$(echo "$best_map * 10000" | bc 2>/dev/null | cut -d'.' -f1)
            
            if [ "$current_int" -gt "$best_int" ] 2>/dev/null; then
                best_map=$map50
                best_model=$model_name
            fi
        fi
    fi
done

echo "🏆 BEST MODEL:"
echo "=============="
if [ ! -z "$best_model" ]; then
    echo "   $best_model"
    echo "   mAP50: $best_map"
    echo "   Path: ./runs/detect/runs/train/$best_model/weights/best.pt"
else
    echo "   Could not determine (check manually)"
fi
