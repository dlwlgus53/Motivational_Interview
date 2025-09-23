import json
import random

# 입력 데이터 파일 경로
input_file = "/home/jihyunlee/MI/AnnoMI/generated/step2_annomi.json"
train_file = "/home/jihyunlee/MI/AnnoMI/generated/train.json"
test_file = "/home/jihyunlee/MI/AnnoMI/generated/test.json"

# 랜덤 시드 고정 (재현 가능)
random.seed(42)

# 데이터 불러오기
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 조건에 맞는 데이터 추출
eligible_for_test = [
    d for d in data 
    if d.get("mi_quality") == "high" and len(d.get("utterances", [])) <= 60
]

# 조건에 맞는 데이터에서 50개 샘플링
if len(eligible_for_test) < 50:
    raise ValueError(f"조건에 맞는 데이터가 부족합니다. {len(eligible_for_test)}개만 존재합니다.")

test_data = random.sample(eligible_for_test, 50)

# train 데이터 = 전체 - test 데이터
test_ids = {id(d) for d in test_data}  # 객체 고유 ID로 구분
train_data = [d for d in data if id(d) not in test_ids]

# 저장
with open(train_file, "w", encoding="utf-8") as f:
    json.dump(train_data, f, indent=2, ensure_ascii=False)

with open(test_file, "w", encoding="utf-8") as f:
    json.dump(test_data, f, indent=2, ensure_ascii=False)

print(f"Train 데이터: {len(train_data)}개, Test 데이터: {len(test_data)}개 저장 완료!")
