import json

input_path = "./instruct_dataset.jsonl"
output_path = "./instruct_dataset_fixed.jsonl"

with open(input_path, "r", encoding="utf-8") as infile, open(
    output_path, "w", encoding="utf-8"
) as outfile:
    for line in infile:
        try:
            item = json.loads(line)
            age = item["output"].get("age")
            if isinstance(age, str):
                # 숫자처럼 생겼으면 float/int로 변환 시도
                if age.isdigit():
                    item["output"]["age"] = int(age)
                else:
                    try:
                        item["output"]["age"] = float(age)
                    except:
                        item["output"]["age"] = None  # 완전 이상하면 제거
            outfile.write(json.dumps(item, ensure_ascii=False) + "\n")
        except Exception as e:
            print("❌ Skipping bad line:", e)
