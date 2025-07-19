import asyncio
import aiohttp

# 模拟2个用户的请求
USER_REQUESTS = [
    {"user_id": "user_a", "query": "hi"},
    {"user_id": "user_b", "query": "hello"},
    {"user_id": "user_b", "query": "推荐一部科幻电影"}
]

async def send_request(session, data):
    async with session.post("http://localhost:8000/generate", json=data) as response:
        result = await response.json()
        # 客户端根据返回的user_id确认是自己的结果
        print(f"用户 {result['user_id']} 的回复：{result['reply']}")

async def main():
    async with aiohttp.ClientSession() as session:
        # 并发发送两个请求
        tasks = [send_request(session, data) for data in USER_REQUESTS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
