import asyncio
import aiohttp
import os
import random
import time
from nemoguardrails.ryan_logger import ryan_log

USER_REQUESTS = [
    {"user_id": "user_a", "query": "hi"},
    {"user_id": "user_b", "query": "hello"},
    # {"user_id": "user_c", "query": "推荐一部科幻电影"}
]

async def send_request(session, data):
    ryan_log.debug(f"User: {data['query']}")
    start_time = time.time()
    try:
        host = os.getenv("HOST", "localhost")
        port = os.getenv("PORT", "8080")
        base_url = "http://" + host + ":" + port
        async with session.post(base_url + "/generate", json=data) as response:
            result = await response.json()
            time_cost = (time.time() - start_time) * 1000
            ryan_log.info(f"Bot({result['user_id']}): {result['reply']} (latency: {time_cost}ms)")
    except Exception as e:
        ryan_log.error(f"Request failed: {str(e)}")


async def main():
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(100)

        async def limited_send_request(session, data):
            async with semaphore:
                await asyncio.sleep(random.random())
                return await send_request(session, data)

        for i in range(10):
            tasks = [limited_send_request(session, data) for data in USER_REQUESTS]
            await asyncio.gather(*tasks)

        while True:
            user_input = input("User: ")
            if user_input.lower() == "quit":
                break

            data = {"user_id": "user_input", "query": user_input}
            await send_request(session, data)


if __name__ == "__main__":
    asyncio.run(main())
