import os
import json
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

with open("test_data.json", "r", encoding="utf-8") as f:
    books = json.load(f)

dataset = []

for book in books[:3]:  # 테스트용 3개만
    title = book["title"]
    description = book["description"]

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

        dataset.append(
            {
                "instruction": "도서 설명을 보고 추천 조건을 추출하세요.",
                "input": f"'{title}' 책을 아이에게 읽어주고 싶은데, 어떤 책인지 알려주세요.\n\n설명: {description}",
                "output": output,
            }
        )

    except Exception as e:
        print(f"❌ Error for '{title}':", e)
        continue

with open("instruct_dataset.jsonl", "w", encoding="utf-8") as f:
    for item in dataset:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("✅ instruct_dataset.jsonl 생성 완료.")
