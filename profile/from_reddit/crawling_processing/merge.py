import os
import json
from transformers import pipeline
from tqdm import tqdm

# ====== 경로 설정 ======
INPUT_FOLDER = "../done4"
OUTPUT_PATH = "../reddit_posts_masked4.json"

# ====== PII 모델 & 리스트 ======
gen = pipeline("token-classification", "lakshyakh93/deberta_finetuned_pii")
PII_LIST = [
    "EMAIL","BITCOINADDRESS","ETHEREUMADDRESS","ACCOUNTNAME","IBAN","ACCOUNTNUMBER",
    "BIC","IPV4","ZIPCODE","IPV6","CREDITCARDNUMBER","VEHICLEVIN","PASSWORD",
    "PHONE_NUMBER","SSN","LITECOINADDRESS","MAC","CREDITCARDISSUER","CREDITCARDCVV",
    "IP","SEX","PIN",
]

def find_pii_spans(text: str):
    """
    텍스트에서 PII 스팬을 찾아 (start, end) 인덱스 목록을 반환.
    겹치는 스팬은 병합.
    """
    preds = gen(str(text), aggregation_strategy="first")
    spans = [
        (p["start"], p["end"])
        for p in preds
        if p.get("entity_group") in PII_LIST and isinstance(p.get("start"), int) and isinstance(p.get("end"), int)
    ]
    if not spans:
        return []

    # 겹치는 구간 병합
    spans.sort()
    merged = []
    cur_s, cur_e = spans[0]
    for s, e in spans[1:]:
        if s <= cur_e:  # overlap
            cur_e = max(cur_e, e)
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = s, e
    merged.append((cur_s, cur_e))
    return merged

def mask_text(text: str, mask_token: str = "[masking]") -> str:
    """
    주어진 텍스트에서 PII 스팬을 [masking] 으로 치환.
    """
    if not isinstance(text, str) or not text:
        return text
    spans = find_pii_spans(text)
    if not spans:
        return text

    # 뒤에서부터 치환(인덱스 어긋남 방지)
    out = text
    for s, e in reversed(spans):
        out = out[:s] + mask_token + out[e:]
    return out

def mask_any(obj):
    """
    사전/리스트 내부의 모든 문자열 값을 재귀적으로 [masking].
    Reddit 스키마에 종속적이지 않아 향후 필드 추가에도 안전.
    """
    if isinstance(obj, dict):
        return {k: mask_any(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [mask_any(v) for v in obj]
    elif isinstance(obj, str):
        return mask_text(obj)
    else:
        return obj

def merge_json_files_with_mask(folder_path: str, output_path: str):
    merged = {}
    total_items = 0
    total_comments_count = 0

    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".json")])
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        print(f"Reading file: {filename}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 각 항목 마스킹 후 병합
        for cid, item in tqdm(data.items(), desc=f"masking {filename}", unit="post"):
            masked_item = mask_any(item)

            # 코멘트 개수 세기(리스트가 있으면 길이, 없으면 num_comments 사용)
            if isinstance(item, dict):
                if isinstance(item.get("comments"), list):
                    total_comments_count += len(item["comments"])
                elif isinstance(item.get("num_comments"), int):
                    total_comments_count += item["num_comments"]

            merged[cid] = masked_item
            total_items += 1

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(merged, out, indent=4, ensure_ascii=False)

    print(f"All JSON files merged + masked -> {output_path}")
    print(f"Total entries: {len(merged)} (seen: {total_items})")
    print(f"Total comments (sum): {total_comments_count}")

if __name__ == "__main__":
    merge_json_files_with_mask(INPUT_FOLDER, OUTPUT_PATH)
