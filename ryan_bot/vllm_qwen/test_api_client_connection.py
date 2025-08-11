# Minimal test request
import httpx
import asyncio

async def test_connection():
    async with httpx.AsyncClient() as client:
        r = await client.post("http://cn005.crg.cerence.net:8010/generate",
                            json={
                                "user_id": "test_user",
                                "query": "test",
                                "messages": [{"role": "user", "content": "client测试"}]
                            })
        print(r.status_code, r.text)

if __name__ == "__main__":
    asyncio.run(test_connection())