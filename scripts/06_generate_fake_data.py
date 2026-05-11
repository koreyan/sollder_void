import os
import torch
import torch.nn as nn
import torchvision
import cv2
import numpy as np

LATENT_DIM = 100
CHANNELS = 1
IMG_SIZE = 128
NUM_FAKE_IMAGES = 500
OUTPUT_DIR = 'data/generated'
LABELS_DIR = 'data/labels'
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LABELS_DIR, exist_ok=True)

class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.main = nn.Sequential(
            nn.ConvTranspose2d(LATENT_DIM, 512, 4, 1, 0, bias=False),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            nn.ConvTranspose2d(512, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            nn.ConvTranspose2d(256, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.ConvTranspose2d(128, 64, 4, 2, 1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.ConvTranspose2d(64, 32, 4, 2, 1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            nn.ConvTranspose2d(32, CHANNELS, 4, 2, 1, bias=False),
            nn.Tanh()
        )

    def forward(self, input):
        return self.main(input)

netG = Generator().to(device)
netG.load_state_dict(torch.load('models/generator/dcgan_g.pt', map_location=device))
netG.eval()

# 가상 이미지 생성 및 자동 라벨링 적용
print(f"Generating {NUM_FAKE_IMAGES} virtual defect images...")
with torch.no_grad():
    for i in range(NUM_FAKE_IMAGES):
        noise = torch.randn(1, LATENT_DIM, 1, 1, device=device)
        fake = netG(noise).detach().cpu().squeeze().numpy()
        
        # [-1, 1] 범위를 [0, 255] 픽셀 값으로 변환
        fake_img = ((fake + 1) / 2.0 * 255).astype(np.uint8)
        
        # 자동 라벨링 알고리즘 (Phase 1과 동일, 단 128x128 크기에 맞춰 면적 필터 조정)
        blurred = cv2.GaussianBlur(fake_img, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 5)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        base_name = f"fake_void_{i:04d}"
        img_path = os.path.join(OUTPUT_DIR, f"{base_name}.jpg")
        label_path = os.path.join(LABELS_DIR, f"{base_name}.txt")
        
        cv2.imwrite(img_path, fake_img)
        
        h_img, w_img = fake_img.shape
        with open(label_path, 'w') as f:
            for cnt in contours:
                area = cv2.contourArea(cnt)
                # 128x128 캔버스 기준이므로 최소/최대 면적을 더 작게 조정
                if 2 < area < 100:
                    x, y, w, h = cv2.boundingRect(cnt)
                    x_center = (x + w / 2) / w_img
                    y_center = (y + h / 2) / h_img
                    w_norm = w / w_img
                    h_norm = h / h_img
                    f.write(f"0 {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n")

# Proposed 모델 학습을 위한 데이터 스플릿 병합 (실제 Train + 가상 500장)
SPLITS_DIR = 'data/splits'
train_real_path = os.path.join(SPLITS_DIR, 'train.txt')
train_proposed_path = os.path.join(SPLITS_DIR, 'train_proposed.txt')

with open(train_real_path, 'r') as f:
    train_real = f.read().splitlines()

fake_files = [os.path.abspath(os.path.join(OUTPUT_DIR, f"fake_void_{i:04d}.jpg")) for i in range(NUM_FAKE_IMAGES)]
train_proposed = train_real + fake_files

with open(train_proposed_path, 'w') as f:
    for p in train_proposed:
        f.write(p + '\n')

yaml_proposed = f"""
train: {os.path.abspath(train_proposed_path)}
val: {os.path.abspath(os.path.join(SPLITS_DIR, 'val.txt'))}
test: {os.path.abspath(os.path.join(SPLITS_DIR, 'test.txt'))}

nc: 1
names: ['Void']
"""
with open('data/data_proposed.yaml', 'w') as f:
    f.write(yaml_proposed)

print(f"\n=== 가상 불량 데이터 생성 완료 ===")
print(f"생성된 파일 수: {NUM_FAKE_IMAGES} 장 (이미지 및 YOLO BBox 라벨)")
print("새로운 데이터 구성 파일 'data/data_proposed.yaml' 이 생성되었습니다.")
print(f"기존 Train({len(train_real)}) + Fake({NUM_FAKE_IMAGES}) = Proposed Train({len(train_proposed)})")
