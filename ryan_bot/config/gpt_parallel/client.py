import asyncio
import aiohttp

# 模拟2个用户的请求
USER_REQUESTS = [
    {"user_id": "user_a", "query": "hi"},
    {"user_id": "user_b", "query": "hello"}
    # {"user_id": "user_b", "query": "推荐一部科幻电影"}
]

async def send_request(session, data):
    print(f"发送请求: {data}")
    try:
        async with session.post("http://10.16.118.41:8080/generate", json=data) as response:
            result = await response.json()
            print(f"用户 {result['user_id']} 的回复：{result['reply']}")
    except Exception as e:
        print(f"请求失败: {str(e)}")

async def main():
    async with aiohttp.ClientSession() as session:
        # 1. 并发发送两个请求
        tasks = [send_request(session, data) for data in USER_REQUESTS]
        await asyncio.gather(*tasks)

        # 2. 进入交互模式
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                break

            data = {"user_id": "user_input", "query": user_input}
            await send_request(session, data)

if __name__ == "__main__":
    asyncio.run(main())
