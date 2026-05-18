


# import httpx
# from app.core import MISTRAL_API_KEY

# MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

# async def get_llm_response(user_message: str) -> str:
#     headers = {
#         "Authorization": f"Bearer {MISTRAL_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     body = {
#         "model": "mistral-small-latest",
#         "messages": [
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": user_message}
#         ]
#     }
#     async with httpx.AsyncClient(timeout=60.0) as client:
#         response = await client.post(MISTRAL_URL, headers=headers, json=body)
#         data = response.json()
#         if "choices" not in data:
#             raise Exception(f"Unexpected response: {data}")
#         return data["choices"][0]["message"]["content"]

# async def stream_llm_response(user_message: str):
#     headers = {
#         "Authorization": f"Bearer {MISTRAL_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     body = {
#         "model": "mistral-small-latest",
#         "messages": [
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": user_message}
#         ],
#         "stream": True  # 👈 enable streaming
#     }

#     async with httpx.AsyncClient(timeout=60.0) as client:
#         async with client.stream("POST", MISTRAL_URL, headers=headers, json=body) as response:
#             async for line in response.aiter_lines():
#                 if line.startswith("data: "):
#                     chunk = line[6:]  # remove "data: " prefix
#                     if chunk.strip() == "[DONE]":
#                         break
#                     try:
#                         import json
#                         data = json.loads(chunk)
#                         delta = data["choices"][0]["delta"]
#                         if "content" in delta and delta["content"]:
#                             yield delta["content"]  # yield each token
#                     except:
#                         continue


import json  # at top of file

async def stream_llm_response(user_message: str):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ],
        "stream": True
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", MISTRAL_URL, headers=headers, json=body) as response:
            if response.status_code != 200:
                error_body = await response.aread()
                print("❌ Mistral stream error:", response.status_code, error_body)
                yield f"[ERROR: Mistral returned {response.status_code}]"
                return

            async for line in response.aiter_lines():
                print("RAW LINE:", repr(line))   # 👈 temporary debug
                if not line.startswith("data: "):
                    continue
                chunk = line[6:]
                if chunk.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                    delta = data["choices"][0]["delta"]
                    content = delta.get("content")
                    if content:
                        yield content
                except json.JSONDecodeError as e:
                    print("⚠️ parse fail:", repr(chunk), e)
                    continue