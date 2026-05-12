# 로컬 실행 가이드 (Local Execution Guide)

이 문서는 **Live AI Solder Void Detection System**을 로컬 환경에서 설치하고 실행하기 위한 단계별 가이드를 제공함.

---

## 1. 환경 요구 사양 (System Requirements)

프로젝트를 단순히 실행만 할 것인지, 아니면 모델을 직접 재학습할 것인지에 따라 요구 사양이 다름.

### A. 서비스 실행 전용 (Inference Only)
- **목적**: 완성된 모델(`best.pt`)을 이용해 대시보드를 구동하고 실시간 탐지 테스트를 수행함.
- **CPU**: 일반적인 듀얼코어 이상의 CPU
- **RAM**: **최소 4GB RAM** (Next.js 웹 서버 + FastAPI AI 서버 동시 구동 가능)
- **GPU**: 불필요 (CPU만으로도 YOLOv8 실시간 추론 가능)

### B. 모델 재학습 및 개발용 (Training & Development)
- **목적**: GAN을 이용해 데이터를 새로 생성하거나, YOLO 모델을 50 Epoch 이상 심층 학습시킴.
- **CPU**: 쿼드코어 이상의 고성능 CPU 권장
- **RAM**: **최소 16GB RAM** (대량의 데이터 로드 및 학습 프로세스 안정성 확보)
- **GPU**: **NVIDIA GPU 권장** (CUDA 지원 시 학습 속도 10배 이상 향상)
- **Storage**: 10GB 이상의 여유 공간 (데이터셋 및 학습 로그 저장)

---

## 2. 백엔드 설정 (AI Server)
FastAPI 기반의 AI 추론 서버를 먼저 실행해야 함.

### venv 생성 및 라이브러리 설치
```bash
# 프로젝트 루트 디렉토리에서 수행
python3 -m venv venv
source venv/bin/activate

# 필수 라이브러리 설치
pip install -r backend/requirements.txt
```

### AI 서버 실행
```bash
# backend 디렉토리의 main.py 실행 (루트에서 실행 권장)
python3 backend/main.py
```
- 서버는 기본적으로 `http://localhost:8000`에서 동작함.
- 실행 시 `models/` 폴더 내의 YOLO 가중치(`best.pt`)를 자동으로 로드함.

---

## 3. 프론트엔드 설정 (Web Dashboard)
Next.js 기반의 인터랙티브 대시보드를 실행함.

### 의존성 설치
```bash
cd web
npm install
```

### 개발 서버 실행
```bash
npm run dev
```
- 웹 대시보드는 `http://localhost:3000`에서 확인할 수 있음.

---

## 4. 프로젝트 구조 및 실행 흐름

### 주요 디렉토리
- `backend/`: FastAPI 추론 엔진 및 이미지 처리 로직
- `web/`: Next.js 대시보드 (App Router 기반)
- `models/`: 학습된 YOLOv8 모델 가중치 저장소
- `scripts/`: 데이터 전처리 및 모델 학습용 유틸리티

### 데이터 흐름
1. 사용자가 웹 UI(`localhost:3000`)에서 검사 이미지를 업로드하거나 실시간 감지 페이지로 이동함.
2. 웹 서버가 백엔드 API(`localhost:8000/predict`)로 이미지 데이터를 전송함.
3. 백엔드에서 YOLOv8 모델이 Void(기포)를 탐지하고 면적 비율을 계산함.
4. 결과값(BBox 좌표, Verdict)이 다시 웹 UI에 실시간으로 시각화됨.

---

## 5. 문제 해결 (Troubleshooting)

### 포트 충돌
- 8000번 포트(백엔드) 또는 3000번 포트(프론트엔드)가 이미 사용 중인 경우, 프로세스를 종료하거나 설정을 변경해야 함.

### 모델 로드 실패
- `models/` 디렉토리에 `best.pt` 파일이 있는지 확인함. 만약 없다면 학습 스크립트(`scripts/09_train_proposed.py`)를 통해 먼저 학습을 진행하거나 가중치 파일을 배치해야 함.

### CORS 에러
- 백엔드 `main.py`에 프론트엔드 도메인(`localhost:3000`)에 대한 CORS 설정이 되어 있는지 확인함. (현재 기본 적용됨)
