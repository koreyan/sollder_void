import os

# 1. processed 폴더를 images 폴더로 이름 변경
if os.path.exists('data/processed') and not os.path.exists('data/images'):
    os.rename('data/processed', 'data/images')
    print("Renamed 'data/processed' to 'data/images'")

# 2. 데이터 분할 txt 파일들의 경로 일괄 수정
splits = ['data/splits/train.txt', 'data/splits/val.txt', 'data/splits/test.txt', 'data/splits/train_proposed.txt']
for split in splits:
    if os.path.exists(split):
        with open(split, 'r') as f:
            lines = f.readlines()
        with open(split, 'w') as f:
            for line in lines:
                f.write(line.replace('/data/processed/', '/data/images/'))
        print(f"Updated paths in {split}")

print("\n=== YOLO 호환성 구조 변경 완료 ===")
