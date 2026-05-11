import os
import torch
import torch.nn as nn
import io
import base64
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from ultralytics import YOLO
import torchvision.transforms as transforms

app = FastAPI(title="Solder Void AI Backend")

# 프론트엔드(Next.js) 접속 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AI 모델 설정 ---
LATENT_DIM = 100
IMG_SIZE = 128
CHANNELS = 1
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# DCGAN Generator 클래스 정의
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

# 모델 전역 로드
generator = Generator().to(DEVICE)
gen_path = "models/generator/dcgan_g.pt"
if os.path.exists(gen_path):
    generator.load_state_dict(torch.load(gen_path, map_location=DEVICE))
    generator.eval()
    print("DCGAN Generator Loaded.")

detector_path = "runs/detect/models/detector/proposed/weights/best.pt"
yolo_model = YOLO(detector_path)
print("YOLOv8 Detector Loaded.")

# --- 유틸리티 함수 ---
def pil_to_base64(img: Image.Image):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# --- API 엔드포인트 ---

@app.get("/")
def read_root():
    return {"message": "Solder Void AI API is running"}

@app.post("/api/generate")
async def generate_image():
    """DCGAN을 이용한 실시간 불량 데이터 생성"""
    with torch.no_grad():
        noise = torch.randn(1, LATENT_DIM, 1, 1, device=DEVICE)
        fake_tensor = generator(noise).detach().cpu()
        
        # [-1, 1] -> [0, 255]
        fake_img = fake_tensor[0][0].numpy()
        fake_img = ((fake_img + 1.0) * 127.5).astype(np.uint8)
        
        img = Image.fromarray(fake_img, mode='L')
        # 시연을 위해 640x640으로 확대
        img = img.resize((640, 640), Image.LANCZOS)
        
        base64_str = pil_to_base64(img)
        
    return {
        "status": "success",
        "image_base64": f"data:image/jpeg;base64,{base64_str}"
    }

@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    """YOLOv8을 이용한 실시간 불량 탐지 및 판독 (감도 극대화)"""
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    
    # [개선] 선명도 및 대비 동시 보정
    from PIL import ImageEnhance
    img = ImageEnhance.Contrast(img).enhance(1.8) # 대비 대폭 향상
    img = ImageEnhance.Sharpness(img).enhance(2.0) # 선명도 대폭 향상
    
    # YOLO 추론 (conf를 0.05로 매우 낮게 설정)
    results = yolo_model(img, conf=0.05)[0]
    
    boxes = []
    total_void_area = 0
    img_w, img_h = img.size
    
    for box in results.boxes:
        x_c, y_c, w, h = box.xywh[0].tolist()
        conf = float(box.conf[0])
        
        total_void_area += (w * h)
        
        boxes.append({
            "x": x_c - w/2,
            "y": y_c - h/2,
            "width": w,
            "height": h,
            "confidence": conf
        })
    
    # Void Ratio 계산
    void_ratio = (total_void_area / (img_w * img_h)) * 100
    
    # 판정 결과 (시연 최적화: 0.5% 초과 또는 탐지 객체 존재 시 불량)
    verdict = "Defect" if (void_ratio > 0.5 or len(boxes) > 0) else "Normal"
    
    return {
        "status": "success",
        "verdict": verdict,
        "void_ratio_percent": round(void_ratio, 2),
        "boxes": boxes,
        "count": len(boxes)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
