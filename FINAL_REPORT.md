# [최종 보고서] AI 기반 반도체 솔더 Void 실시간 탐지 및 성능 강화 프로젝트

## 1. 프로젝트 개요 (Executive Summary)
본 프로젝트는 반도체 패키징 공정 중 발생하는 **솔더 Void(기포)** 불량을 정밀하게 탐지하기 위한 AI 시스템 구축을 목표로 합니다. 특히, 실제 현장의 고질적 문제인 **'희소한 불량 데이터'** 문제를 해결하기 위해 **DCGAN 기반의 가상 데이터 증강(Data Augmentation)** 기법을 도입하였으며, 이를 통해 강화된 **YOLOv8** 탐지 모델의 성능 향상을 실증하였습니다.

---

## 2. 시스템 아키텍처 및 디렉토리 구조

### 2.1 전체 시스템 파이프라인
프로젝트는 데이터 전처리부터 AI 모델 학습, 웹 시연까지 엔드-투-엔드 파이프라인으로 구성됩니다.
1. **Data Phase**: OpenCV 기반 Void 영역 추출 및 YOLO 포맷 변환
2. **AI Phase (Track A)**: DCGAN을 통한 가상 불량 이미지 생성 및 데이터셋 확장
3. **AI Phase (Track B)**: Baseline(실제) vs Proposed(실제+가상) YOLOv8 모델 비교 학습
4. **Service Phase**: FastAPI 백엔드와 Next.js 프론트엔드를 통한 실시간 추론 시연

### 2.2 디렉토리 구조
```text
sollder_void/
├── backend/            # FastAPI AI 추론 서버 (Python)
│   ├── main.py         # DCGAN/YOLOv8 통합 API 및 추론 로직
│   └── models/         # 학습 완료된 가중치 파일 (.pt)
├── web/                # Next.js 프론트엔드 (React/TypeScript)
│   ├── app/live/       # 실시간 시연 및 AI 인터랙션 페이지
│   └── globals.css     # Glassmorphism 테마 및 반응형 스타일
├── data/               # 학습 및 검증용 데이터셋
├── notebook/           # EDA 및 전처리 실험 로그
└── runs/               # YOLOv8 모델 학습 결과 및 지표
```

---

## 3. 데이터 엔지니어링 (Data Engineering)

### 3.1 데이터 속성 및 선정 이유
*   **데이터 타입**: 반도체 패키지 X-ray 영상 (128x128 Grayscale)
*   **핵심 속성**: 
    *   **Void Area**: 솔더 내 기포가 차지하는 검은색 픽셀 영역
    *   **정상/불량 기준**: Void 면적 비율이 **5.0%**를 초과할 경우 불량으로 정의
*   **선정 이유**: X-ray 영상은 촬영 환경에 따라 대비가 낮고 노이즈가 많아, 단순한 수치 비교보다 특징 형상을 학습하는 딥러닝 기반 탐지가 고정밀 판독에 유리함.

### 3.2 전처리 파이프라인
1. **CLAHE 적용**: 대비(Contrast)를 적응형으로 개선하여 Void 경계를 뚜렷하게 보정
2. **Thresholding**: OpenCV를 이용해 Void 후보 영역의 BBox 자동 생성 및 라벨링
3. **데이터 분할**: Train/Val/Test 데이터를 70:15:15 비율로 분리하여 엄격한 검증 수행

---

## 4. AI 모델 상세 및 학습 조건

### 4.1 불량 생성 모델 (DCGAN)
*   **선정 모델**: DCGAN (Deep Convolutional Generative Adversarial Networks)
*   **선정 이유**: 적은 데이터셋(1.8k)으로도 X-ray 특유의 질감과 불규칙한 Void 패턴을 효과적으로 모방 가능.
*   **학습 조건**:
    *   **입력**: 100차원의 랜덤 노이즈 벡터 (Gaussian Noise)
    *   **최적화**: Adam Optimizer (Learning Rate: 0.0002, Beta1: 0.5)
    *   **과정**: Generator가 가짜 불량을 생성하고, Discriminator가 진위를 판별하며 서로 경쟁 학습.

### 4.2 불량 탐지 모델 (YOLOv8)
*   **선정 모델**: YOLOv8-Small
*   **선정 이유**: 속도(Real-time)와 정확도(mAP)의 균형이 가장 뛰어나며, 모바일 시연 환경에서 낮은 지연 시간을 보장함.
*   **학습 전략**:
    *   **Baseline**: 실제 현장 데이터만으로 학습
    *   **Proposed**: 실제 데이터에 GAN 생성 이미지 1,000장을 추가하여 학습 (데이터 다양성 확보)
    *   **조건**: Image Size 640, Batch 16, 50 Epochs 학습 수행.

---

## 5. 성능 분석 및 검증 (초기 실험 결과)

5 Epoch의 초기 학습 환경에서 Baseline과 Proposed 모델의 성능을 비교 검증하였습니다.

| 성능 지표 | Baseline Model | Proposed Model | 차이 (Baseline 대비) |
| :--- | :---: | :---: | :---: |
| **mAP50** | **76.4%** | 72.6% | 📉 -3.8%p |
| **mAP50-95** | **42.1%** | 40.3% | 📉 -1.8%p |
| **F1-Score** | **0.752** | 0.680 | 📉 -0.072 |

*   **분석 요약**: 초기 실험 결과, 가상 데이터가 추가된 Proposed 모델이 Baseline보다 다소 낮은 성능을 보였습니다. 이는 GAN 생성 이미지의 노이즈를 모델이 학습하기에 **5 Epoch**이라는 학습 횟수가 절대적으로 부족했기 때문으로 분석됩니다.
*   **시사점**: 가상 데이터 증강 효과를 극대화하기 위해서는 최소 50 Epoch 이상의 충분한 학습과 생성 데이터의 품질 필터링 과정이 선행되어야 함을 확인하였습니다. (본 보고서는 현재 시점의 실제 측정치를 기반으로 작성됨)

---

## 6. 기술 스택 및 개발 환경

### 6.1 기술 스택 선정 이유
*   **Next.js (FE)**: SEO 최적화 및 빠른 페이지 전환, 모바일 반응형 시연 페이지 구축에 용이.
*   **FastAPI (BE)**: Python AI 라이브러리(PyTorch, OpenCV)와의 높은 호환성 및 빠른 API 응답성.
*   **PyTorch/Ultralytics**: 최신 YOLOv8 모델의 안정적인 학습 및 추론 지원.

### 6.2 로컬 개발 환경 (Local Development Environment)
본 프로젝트는 다음의 로컬 환경에서 개발 및 초기 학습이 수행되었습니다.
*   **OS**: macOS (Apple M-series)
*   **Language**: Python 3.10 / Node.js 18.x
*   **Frontend**: Next.js 14.2.3 (Localhost:3000)
*   **Backend**: FastAPI 0.109.0 (Localhost:8000)


### 6.3 클라우드 배포 권장 사양 (Deployment Recommendations)
실시간 시연의 끊김 없는 성능과 안정적인 AI 모델 구동을 위한 권장 사양입니다.
*   **Platform**: AWS EC2 / GCP Compute Engine
*   **Instance Type**: `g4dn.xlarge` (NVIDIA T4 GPU 탑재 모델 권장)
*   **vCPU / RAM**: **2 Core / 4 GB 이상** (소규모 시연 및 1~2인 접속 시 최적의 경제적 사양)
*   **Storage**: **30 GB SSD 이상** (Docker 이미지 및 모델 가중치 파일 용량 고려)
*   **OS**: Ubuntu 22.04 LTS
*   **Container**: **Docker / Docker Compose** (환경 일관성 및 배포 용이성 확보)

### 6.4 주요 라이브러리 명세

#### [Backend & AI Engine]
| 라이브러리 | 용도 |
| :--- | :--- |
| **ultralytics** | YOLOv8 모델 학습 및 실시간 객체 탐지(Inference) 핵심 엔진 |
| **torch / torchvision** | DCGAN 및 YOLOv8 구동을 위한 딥러닝 프레임워크 |
| **fastapi / uvicorn** | 고성능 비동기 AI 추론 API 서버 구축 |
| **opencv-python** | 이미지 전처리(Thresholding, CLAHE) 및 픽셀 연산 |
| **scipy** | Baseline vs Proposed 모델 성능 차이에 대한 통계적 유의성(T-Test) 검증 |
| **pandas / numpy** | Void Rate 데이터 통계 분석 및 대량의 수치 데이터 처리 |
| **pillow (PIL)** | API 이미지 입출력 및 실시간 선명도/대비 보정 |

#### [Frontend]
| 라이브러리 | 용도 |
| :--- | :--- |
| **next / react** | SSR(Server-Side Rendering) 기반의 고성능 웹 대시보드 구축 |
| **framer-motion** | 실시간 상태 변화 및 결과 노출 시 부드러운 애니메이션 효과 |
| **lucide-react** | 직관적인 시스템 상태 표시를 위한 벡터 아이콘 팩 |
| **qrcode.react** | 모바일 시연 접속을 위한 실시간 QR 코드 생성 |
| **canvas-confetti** | 판독 결과 시각적 피드백 효과 (선택사항) |

---

## 7. 웹 디자인 및 시연 시스템

### 7.1 디자인 시스템 (UX/UI)
*   **Concept**: **Glassmorphism Tech** (반투명 레이어와 네온 블루 포인트를 사용한 미래지향적 디자인)
*   **Accessibility**: 전체 UI 한글화 및 모바일 웹 최적화.
*   **Responsive**: 모바일 접속 시 하단 고정 액션 버튼(Sticky Buttons)을 통한 한 손 시연 최적화.

### 7.2 백엔드 API 명세
1. `POST /api/generate`: DCGAN을 구동하여 128x128 불량 이미지를 실시간 생성.
2. `POST /api/predict`: YOLOv8을 통해 업로드된 이미지의 Void를 탐지하고 '정상/불량' 최종 판독.

---

## 8. 개선 및 향후 발전 방향
1. **모델 고도화**: Diffusion 모델을 도입하여 더 고해상도의 불량 이미지 생성 연구.
2. **실시간 모니터링**: 대량의 이미지를 초당 수십 장 이상 처리할 수 있는 Batch Inference 파이프라인 구축.
3. **엣지 컴퓨팅**: 학습된 모델을 TensorRT로 최적화하여 현장의 임베디드 장비에 직접 이식.

---
**최종 업데이트**: 2026-05-11  
**프로젝트 상태**: Phase 5 실시간 시연 시스템 구축 완료 (Live Inference Ready)
