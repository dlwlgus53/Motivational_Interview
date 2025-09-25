import json
from collections import Counter

# 데이터 불러오기
data_path = "/home/jihyunlee/MI/AnnoMI/generated/test.json"
dataset = json.load(open(data_path))

# dialogue 단위 code 수 세기
codes = []
for dial_item in dataset:
    codes.append(dial_item["stage_resistant"]["pre-contemplation"]["attitude_code"])
    codes.append(dial_item["stage_resistant"]["contemplation"]["attitude_code"])
    codes.append(dial_item["stage_resistant"]["preparation"]["attitude_code"])

# dialogue 수 기준 집계
code_counts = Counter(codes)

# # 결과 저장
# save_path = data_path.replace(".json", "_dialogue_counts.json")
# with open(save_path, "w") as f:
#     json.dump(code_counts, f, indent=4)

print(code_counts)
