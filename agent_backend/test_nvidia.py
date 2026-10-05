from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    timeout=20,
    max_retries=0
)

print("Testing NVIDIA...")
print("API key loaded:", bool(os.getenv("NVIDIA_API_KEY")))

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Say only HELLO"
        }
    ],
    max_tokens=100,
    stream=False
)
print("SUCCESS")
print("\n========== FULL RESPONSE ==========")
print(response)
print("===================================")

print("\nMESSAGE:")
print(response.choices[0].message)

print("\nCONTENT:")
print(repr(response.choices[0].message.content))