import os
import glob
import cv2
import random
import shutil

XRAY_DIR = 'archive/XRay/XRay'
PROCESSED_DIR = 'data/processed'
LABELS_DIR = 'data/labels'
SPLITS_DIR = 'data/splits'

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(LABELS_DIR, exist_ok=True)
os.makedirs(SPLITS_DIR, exist_ok=True)

all_images = glob.glob(os.path.join(XRAY_DIR, '**/*.jpg'), recursive=True)
print(f"Total X-ray images found: {len(all_images)}")

valid_images = []

print("Processing images and generating YOLO labels...")
for idx, img_path in enumerate(all_images):
    img_name = os.path.basename(img_path)
    base_name = os.path.splitext(img_name)[0]
    
    img = cv2.imread(img_path)
    if img is None: continue
    
    h_img, w_img = img.shape[:2]
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 5)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    label_path = os.path.join(LABELS_DIR, f"{base_name}.txt")
    dest_img_path = os.path.join(PROCESSED_DIR, img_name)
    
    with open(label_path, 'w') as f:
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 10 < area < 500:
                x, y, w, h = cv2.boundingRect(cnt)
                x_center = (x + w / 2) / w_img
                y_center = (y + h / 2) / h_img
                w_norm = w / w_img
                h_norm = h / h_img
                f.write(f"0 {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n")
    
    # Copy image to processed directory
    shutil.copy(img_path, dest_img_path)
    valid_images.append(os.path.abspath(dest_img_path))
    
    if (idx + 1) % 300 == 0:
        print(f"[{idx + 1}/{len(all_images)}] processed...")

# Train / Val / Test split (70 / 15 / 15)
print("\nSplitting dataset (70% Train, 15% Val, 15% Test)...")
random.seed(42)
random.shuffle(valid_images)

total = len(valid_images)
train_end = int(total * 0.7)
val_end = int(total * 0.85)

train_files = valid_images[:train_end]
val_files = valid_images[train_end:val_end]
test_files = valid_images[val_end:]

for split_name, files in [('train', train_files), ('val', val_files), ('test', test_files)]:
    with open(os.path.join(SPLITS_DIR, f"{split_name}.txt"), 'w') as f:
        for p in files:
            f.write(p + '\n')

yaml_content = f"""
train: {os.path.abspath(SPLITS_DIR)}/train.txt
val: {os.path.abspath(SPLITS_DIR)}/val.txt
test: {os.path.abspath(SPLITS_DIR)}/test.txt

nc: 1
names: ['Void']
"""
with open('data/data.yaml', 'w') as f:
    f.write(yaml_content)

print("\n=== Dataset Preparation Complete ===")
print(f"Total Valid Images : {total}")
print(f"Train set          : {len(train_files)}")
print(f"Validation set     : {len(val_files)}")
print(f"Test set           : {len(test_files)}")
print(f"YOLO YAML file     : data/data.yaml")
