import asyncio
import os
import traceback
from openai import AsyncOpenAI

async def test_gemini():
    try:
        client = AsyncOpenAI(
            api_key=os.environ.get("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        resp = await client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=10
        )
        print("Response:", resp.choices[0].message.content)
    except Exception as e:
        print("Error:", traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_gemini())
