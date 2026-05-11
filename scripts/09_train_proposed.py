from ultralytics import YOLO
import os

if __name__ == '__main__':
    print("=== Proposed 탐지 모델 학습 시작 ===")
    
    # 결과가 저장될 디렉토리 확인
    os.makedirs('models/detector', exist_ok=True)
    
    # YOLOv8 Small 모델 로드
    model = YOLO('yolov8s.pt')
    
    # 학습 시작
    # data: 실제 데이터 + 생성 데이터가 포함된 data_proposed.yaml
    # epochs: 50
    # imgsz: 640 (원본 유지/자동 리사이즈)
    # device: mps (Mac GPU)
    results = model.train(
        data='data/data_proposed.yaml',
        epochs=5,
        imgsz=640,
        device='mps',
        project='models/detector',
        name='proposed',
        batch=16,
        patience=15 # 성능 개선이 없으면 조기 종료
    )
    
    print("\n=== Proposed 학습 완료! ===")
    print("가중치 저장 위치: models/detector/proposed/weights/best.pt")
