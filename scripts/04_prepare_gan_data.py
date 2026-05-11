import os
import pandas as pd
import shutil

CSV_PATH = 'archive/CrackVoid Ratios/Xray Void Ratio.csv'
PROCESSED_DIR = 'data/processed'
# ImageFolder를 사용하기 위해 클래스별 하위 폴더 구조(defect)를 만듭니다.
GAN_DATA_DIR = 'data/gan_train/defect'
os.makedirs(GAN_DATA_DIR, exist_ok=True)

# CSV 로드 및 결측치/형변환 처리
df = pd.read_csv(CSV_PATH, sep=';')
df['Void rate'] = pd.to_numeric(df['Void rate'].astype(str).str.replace(',', '.'), errors='coerce')
defect_df = df[df['Void rate'] > 0.05]

processed_files = os.listdir(PROCESSED_DIR)

copied = 0
for f in processed_files:
    if not f.endswith('.jpg'):
        continue
        
    # 파일명 구조: XRay_FC-GB2_SAC105_Panel1_LED05_0000TSC.jpg
    parts = f.split('_')
    if len(parts) >= 5:
        led_type = parts[1]
        solder = parts[2]
        panel = int(''.join(filter(str.isdigit, parts[3])))
        led_num = int(''.join(filter(str.isdigit, parts[4])))
        
        # CSV의 불량 리스트에 해당 이미지 조건이 있는지 확인
        match = defect_df[(defect_df['Led Type'] == led_type) & 
                          (defect_df['Solder'] == solder) & 
                          (defect_df['Panel'] == panel) & 
                          (defect_df['LED Number'] == led_num)]
        if not match.empty:
            shutil.copy(os.path.join(PROCESSED_DIR, f), os.path.join(GAN_DATA_DIR, f))
            copied += 1

print(f"=== GAN 학습용 데이터 준비 완료 ===")
print(f"복사된 불량 이미지 수: {copied} 장")
print(f"저장 경로: {GAN_DATA_DIR}")
