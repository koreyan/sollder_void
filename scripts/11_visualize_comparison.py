import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO
import os
import random

def main():
    # Load Models
    baseline_model = YOLO("runs/detect/models/detector/baseline-2/weights/best.pt")
    proposed_model = YOLO("runs/detect/models/detector/proposed/weights/best.pt")

    # Read test images from test.txt
    test_split_file = "data/splits/test.txt"
    if not os.path.exists(test_split_file):
        print(f"File {test_split_file} not found.")
        return
        
    with open(test_split_file, "r") as f:
        test_images = [line.strip() for line in f.readlines() if line.strip()]
        
    if not test_images:
        print("No test images found in the split file.")
        return
        
    # Pick a random image (or first one)
    sample_img_path = test_images[0]
    
    # Run Inference
    res_base = baseline_model(sample_img_path, conf=0.25)
    res_prop = proposed_model(sample_img_path, conf=0.25)
    
    # Get Plot Arrays (BGR)
    img_base = res_base[0].plot()
    img_prop = res_prop[0].plot()
    
    # Convert to RGB for matplotlib
    img_base_rgb = cv2.cvtColor(img_base, cv2.COLOR_BGR2RGB)
    img_prop_rgb = cv2.cvtColor(img_prop, cv2.COLOR_BGR2RGB)
    
    # Plot side by side
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(img_base_rgb)
    axes[0].set_title("Baseline Model")
    axes[0].axis('off')
    
    axes[1].imshow(img_prop_rgb)
    axes[1].set_title("Proposed Model")
    axes[1].axis('off')
    
    plt.tight_layout()
    plt.savefig("comparison_result.png")
    print(f"✅ Saved comparison visualization to comparison_result.png")

if __name__ == "__main__":
    main()
