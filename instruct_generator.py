import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# 원본 데이터 로드
with open("test_data.json", "r", encoding="utf-8") as f:
    books = json.load(f)

# 기존 instruct 데이터 로드 (있다면 이어서 진행)
dataset = []
existing_titles = set()

if os.path.exists("instruct_dataset.jsonl"):
    with open("instruct_dataset.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            dataset.append(item)
            title = item["input"].split("'")[1]
            existing_titles.add(title)

# 새로 처리할 book 범위 (예: 1001~1050)
for book in books[1001:1050]:
    title = book["title"]
    description = book["description"]

    if title in existing_titles:
        continue

    prompt = f"""
아래는 유아용 도서의 설명입니다. 이 설명을 바탕으로 다음과 같은 추천 조건을 JSON 형식으로 추출해 주세요: theme(주제), type(도서 유형), age(추천 연령).

설명:
{description}

출력 형식:
{{"theme": "...", "type": "...", "age": ...}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        output = json.loads(response.choices[0].message.content)

        # ✅ age 정규화
        raw_age = output.get("age")
        normalized_age = None

        if isinstance(raw_age, (int, float)):
            normalized_age = raw_age
        elif isinstance(raw_age, str):
            digits = re.findall(r"\d+", raw_age)
            if digits:
                normalized_age = int(digits[0])  # 가장 먼저 나오는 숫자 사용

        output["age"] = normalized_age

        new_item = {
            "instruction": "도서 설명을 보고 추천 조건을 추출하세요.",
            "input": f"'{title}' 책을 아이에게 읽어주고 싶은데, 어떤 책인지 알려주세요.\n\n설명: {description}",
            "output": output,
        }

        dataset.append(new_item)

        with open("instruct_dataset.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(new_item, ensure_ascii=False) + "\n")

    except Exception as e:
        print(f"❌ Error for '{title}':", e)
        continue

print("✅ instruct_dataset.jsonl 생성 완료 및 age 정규화 적용 완료.")
