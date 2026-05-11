import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 디렉토리 설정
CSV_PATH = 'archive/CrackVoid Ratios/Xray Void Ratio.csv'
RESULTS_DIR = 'results'

os.makedirs(RESULTS_DIR, exist_ok=True)

print("=== 1. 데이터 로드 및 기본 정보 파악 ===")
# CSV는 세미콜론(;)으로 구분됨
df = pd.read_csv(CSV_PATH, sep=';')
df['Void rate'] = pd.to_numeric(df['Void rate'].astype(str).str.replace(',', '.'), errors='coerce')
df = df.dropna(subset=['Void rate'])
print(df.info())
print("\n[상위 5개 데이터]")
print(df.head())

print("\n=== 2. Void Rate (불량률) 통계 ===")
print(df['Void rate'].describe())

# 시각화 1: Void Rate 분포 히스토그램
plt.figure(figsize=(10, 6))
sns.histplot(df['Void rate'], bins=50, kde=True, color='blue')
plt.title('Distribution of Void Rate', fontsize=16)
plt.xlabel('Void Rate (Proportion)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.grid(axis='y', alpha=0.7)
plt.savefig(os.path.join(RESULTS_DIR, 'void_rate_distribution.png'))
plt.close()

# 시각화 2: Solder/LED 타입별 Void Rate 박스플롯
plt.figure(figsize=(12, 6))
sns.boxplot(x='Solder', y='Void rate', data=df)
plt.title('Void Rate by Solder Type', fontsize=16)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'void_rate_by_solder.png'))
plt.close()

print("\n=== 3. 정상/불량 분류 (Threshold 실험) ===")
# 예시 Threshold: 2% (0.02)와 5% (0.05) 기준
threshold_3pct = 0.03
threshold_5pct = 0.05

def_3pct = len(df[df['Void rate'] > threshold_3pct])
def_5pct = len(df[df['Void rate'] > threshold_5pct])
total = len(df)

print(f"Total Samples: {total}")
print(f"Defect Count (Threshold > 3%): {def_3pct} ({def_3pct/total*100:.2f}%)")
print(f"Defect Count (Threshold > 5%): {def_5pct} ({def_5pct/total*100:.2f}%)")

print("\nEDA 완료. 결과 이미지가 'results/' 폴더에 저장되었습니다.")
