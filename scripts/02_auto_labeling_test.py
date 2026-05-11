import cv2
import os
import glob
import numpy as np

# 경로 설정
XRAY_DIR = 'archive/XRay/XRay'
OUTPUT_DIR = 'results/sample_bboxes'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 샘플 10개만 테스트 (하위 폴더 포함)
image_files = glob.glob(os.path.join(XRAY_DIR, '**/*.jpg'), recursive=True)[:10]

print(f"=== 자동 라벨링 테스트 (샘플 {len(image_files)}장) ===")

for img_path in image_files:
    img_name = os.path.basename(img_path)
    
    # 1. 이미지 로드 및 그레이스케일 변환
    img = cv2.imread(img_path)
    if img is None:
        continue
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 노이즈 제거 (블러링)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 2. Otsu Threshold를 이용한 Void 검출
    # X-ray에서 Void는 보통 다른 영역보다 더 밝게 빛나거나 더 어둡습니다.
    # 일반적으로 Void는 밀도가 낮아 X-ray가 잘 통과하여 주변 패드보다 "밝게"(흰색) 나타나는 경우가 많습니다.
    # 하지만 데이터셋 특성에 따라 다를 수 있으므로 cv2.THRESH_BINARY / THRESH_BINARY_INV 여부를 테스트합니다.
    # 여기서는 적응형 임계값(Adaptive Thresholding)을 사용하여 패드 안의 특징을 추출합니다.
    
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 21, 5
    )
    
    # 3. Contour(윤곽선) 추출
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    draw_img = img.copy()
    void_count = 0
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # 면적이 너무 작거나 너무 큰 것은 노이즈/패드 전체로 간주하고 무시 (하이퍼파라미터 조정 필요)
        if 10 < area < 500:
            x, y, w, h = cv2.boundingRect(cnt)
            # 초록색 박스 그리기
            cv2.rectangle(draw_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            void_count += 1
            
    # 결과 이미지 저장
    out_path = os.path.join(OUTPUT_DIR, f"bbox_{img_name}")
    cv2.imwrite(out_path, draw_img)
    print(f"Processed: {img_name} | Detected Voids: {void_count}")

print(f"\n테스트 완료. 결과 이미지가 '{OUTPUT_DIR}'에 저장되었습니다.")
