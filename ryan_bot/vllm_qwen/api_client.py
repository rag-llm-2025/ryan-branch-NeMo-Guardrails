import asyncio
import logging
from typing import Optional, AsyncGenerator
import httpx
import os
from httpx import RequestError
from nemoguardrails.logging.verbose import console
import time

from simple_logger import RyanLogger as logger

# api_server address and port
RAILS_HOST = os.getenv("RAILS_HOST", "localhost")
print("RAILS_HOST:", RAILS_HOST)

API_URL = f"http://{RAILS_HOST}:8010/generate"
HEADERS = {"Content-Type": "application/json"}
MAX_RETRIES = 3

async def stream_request(query: str) -> AsyncGenerator[str, None]:
    """发送流式请求到API服务器"""
    data = {
        "user_id": "test_user",
        "query": query
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(MAX_RETRIES):
            try:
                async with client.stream(
                    "POST",
                    url=API_URL,
                    headers=HEADERS,
                    json=data
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_text():
                        yield chunk
                    break
            except RequestError as e:
                logger.error(f"request failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    yield "Error! request failed, please check the connection or logs"

async def print_response(query):
    start_time = time.time()
    first_chunk = True
    logger.info("Bot: ")
    async for chunk in stream_request(query):
        if first_chunk:
            first_chunk_time = time.time()
            first_chunk = False
        print(chunk, end="", flush=True)

    final_chunk_time = time.time()
    cost_time = (final_chunk_time - start_time) * 1000
    first_response_time = (first_chunk_time - start_time) * 1000
    logger.info(f" (E2E latency={cost_time:.02f}ms, First response latency={first_response_time:.02f}ms)")
    print()
    return cost_time, first_response_time

async def chat_loop():
    # 示例对话
    query = "帮我写一篇关于春天的散文，字数在1000字以上"
    logger.info(f"示例：User: {query}")
    await print_response(query)

    # 用户交互循环
    while True:
        try:
            query = input("User: ")
            logger.info(f"User: {query}")

            if query.lower() == 'quit':
                break

            await print_response(query)
        except KeyboardInterrupt:
            logger.info("\nOver!")
            break

if __name__ == "__main__":
    asyncio.run(chat_loop())