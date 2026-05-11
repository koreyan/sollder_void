"""
Phase 5 Step 1: 웹 시연용 데이터 사전 준비 스크립트
- 테스트셋에서 10개 이미지 선정
- Baseline/Proposed 모델로 추론
- 결과를 JSON으로 저장 (web/public/data/)
"""

import json
import os
import shutil
import random
from ultralytics import YOLO

# === 경로 설정 ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_SPLIT = os.path.join(PROJECT_ROOT, "data/splits/test.txt")
BASELINE_WEIGHTS = os.path.join(PROJECT_ROOT, "runs/detect/models/detector/baseline-2/weights/best.pt")
PROPOSED_WEIGHTS = os.path.join(PROJECT_ROOT, "runs/detect/models/detector/proposed/weights/best.pt")
EVAL_RESULTS = os.path.join(PROJECT_ROOT, "eval_results.json")

# 출력 디렉토리
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "web/public/data")
OUTPUT_IMAGES = os.path.join(OUTPUT_DIR, "images")

NUM_IMAGES = 10
CONF_THRESHOLD = 0.25


def select_images(test_split_path, n=10):
    """테스트셋에서 n개 이미지를 선정"""
    with open(test_split_path, "r") as f:
        all_images = [line.strip() for line in f.readlines() if line.strip()]

    if len(all_images) <= n:
        return all_images

    # 균등 간격으로 선정하여 다양성 확보
    step = len(all_images) // n
    selected = [all_images[i * step] for i in range(n)]
    return selected


def run_inference(model, img_path, conf=0.25):
    """단일 이미지에 대한 추론 결과를 딕셔너리로 반환"""
    results = model(img_path, conf=conf, verbose=False)
    r = results[0]

    boxes = []
    for box in r.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        boxes.append({
            "x": round(x1, 1),
            "y": round(y1, 1),
            "w": round(x2 - x1, 1),
            "h": round(y2 - y1, 1),
            "confidence": round(float(box.conf[0]), 3)
        })

    return {
        "boxes": boxes,
        "total_detections": len(boxes),
        "avg_confidence": round(sum(b["confidence"] for b in boxes) / len(boxes), 3) if boxes else 0
    }


def main():
    print("🚀 Phase 5 Step 1: 웹 시연 데이터 준비 시작")

    # 출력 디렉토리 생성
    os.makedirs(OUTPUT_IMAGES, exist_ok=True)

    # 1. 이미지 선정
    print(f"\n[1/4] 테스트셋에서 {NUM_IMAGES}개 이미지 선정...")
    selected_images = select_images(TEST_SPLIT, NUM_IMAGES)
    print(f"  ✅ {len(selected_images)}개 이미지 선정 완료")

    # 2. 모델 로드
    print("\n[2/4] 모델 로드...")
    baseline_model = YOLO(BASELINE_WEIGHTS)
    proposed_model = YOLO(PROPOSED_WEIGHTS)
    print("  ✅ Baseline + Proposed 모델 로드 완료")

    # 3. 추론 실행 및 이미지 복사
    print(f"\n[3/4] {NUM_IMAGES}개 이미지에 대해 양 모델 추론 중...")
    predictions = {"images": []}

    for idx, img_path in enumerate(selected_images):
        filename = os.path.basename(img_path)
        short_name = f"sample_{idx + 1:02d}.jpg"

        # 이미지 복사
        dst_path = os.path.join(OUTPUT_IMAGES, short_name)
        shutil.copy2(img_path, dst_path)

        # 추론
        baseline_result = run_inference(baseline_model, img_path, CONF_THRESHOLD)
        proposed_result = run_inference(proposed_model, img_path, CONF_THRESHOLD)

        # 이미지 크기 가져오기
        from PIL import Image
        with Image.open(img_path) as im:
            w, h = im.size

        entry = {
            "id": idx + 1,
            "filename": short_name,
            "original_name": filename,
            "width": w,
            "height": h,
            "baseline": baseline_result,
            "proposed": proposed_result
        }
        predictions["images"].append(entry)

        print(f"  [{idx + 1}/{NUM_IMAGES}] {filename}")
        print(f"    Baseline: {baseline_result['total_detections']} detections (avg conf: {baseline_result['avg_confidence']})")
        print(f"    Proposed: {proposed_result['total_detections']} detections (avg conf: {proposed_result['avg_confidence']})")

    # 4. JSON 저장
    print("\n[4/4] JSON 파일 저장...")

    # predictions.json
    pred_path = os.path.join(OUTPUT_DIR, "predictions.json")
    with open(pred_path, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)
    print(f"  ✅ {pred_path}")

    # metrics.json (eval_results.json 기반 + 추가 정보)
    with open(EVAL_RESULTS, "r") as f:
        eval_data = json.load(f)

    metrics = {
        "baseline": {
            **eval_data["baseline"],
            "training_time_sec": 1084,
            "epochs": 5,
            "data_count": 1260,
            "model_name": "YOLOv8s (Real Data Only)"
        },
        "proposed": {
            **eval_data["proposed"],
            "training_time_sec": 1402,
            "epochs": 5,
            "data_count": 1760,
            "model_name": "YOLOv8s (Real + Synthetic)"
        }
    }

    metrics_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"  ✅ {metrics_path}")

    print(f"\n🎉 웹 시연 데이터 준비 완료!")
    print(f"  - 이미지: {OUTPUT_IMAGES} ({NUM_IMAGES}개)")
    print(f"  - 추론 결과: {pred_path}")
    print(f"  - 성능 지표: {metrics_path}")


if __name__ == "__main__":
    main()
