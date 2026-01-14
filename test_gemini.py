import json
from google import genai

client = genai.Client()

# 读取 prompt 模板
with open('config/prompt_template.json', 'r', encoding='utf-8') as f:
    prompt_config = json.load(f)
    prompt_template = prompt_config['prompt_template']

# 读取待审查的代码
with open('code_sample.swift', 'r', encoding='utf-8') as f:
    code = f.read()

# 构建完整的 prompt
prompt = prompt_template.replace('{code}', code)

print("=" * 60)
print("正在审查代码...")
print("=" * 60)

response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=prompt,
)

print("\n审查结果：")
print("=" * 60)
print(response.text)
print("=" * 60)