from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import os
from nemoguardrails import LLMRails, RailsConfig
from contextlib import asynccontextmanager
from nemoguardrails.logging.verbose import console

from simple_logger import RyanLogger as logger
from nemoguardrails.ryan_logger import ryan_log
import time

# api_server address and port
VLLM_HOST = os.getenv("VLLM_HOST", "localhost")
print("VLLM_HOST:", VLLM_HOST)

app = FastAPI()
rails = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    global rails
    config = RailsConfig.from_path("./config")
    config.models[0].parameters["base_url"] = f"http://{VLLM_HOST}:8010/v1"
    config.models[1].parameters["base_url"] = f"http://{VLLM_HOST}:8010/v1"
    rails = LLMRails(config)
    yield
    # 关闭时清理
    if rails:
        del rails

app = FastAPI(lifespan=lifespan)

async def stream_async(prompt: str) -> str:
    """stream async generate response with typewriter effect"""
    start_time = time.time()
    response = []
    first_chunk = True;
    async for chunk in rails.stream_async(messages=[{"role": "user", "content": prompt}]):
        if chunk:  # filter empty content
            if first_chunk:
                first_chunk_time = time.time()
                first_chunk = False
            ryan_log.info(f"stream chunk: {chunk}")
            response.append(chunk)
    final_chunk_time = time.time()
    cost_time = (final_chunk_time - start_time) * 1000
    first_response_time = (first_chunk_time - start_time) * 1000
    # combine and strip the response
    full_response = "".join(response).strip()
    ryan_log.info(f"Final response: {full_response} \n(E2E latency={cost_time:.02f}ms, First response latency={first_response_time:.02f}ms)")
    return full_response

class ChatRequest(BaseModel):
    user_id: str
    query: str

@app.post("/generate")
async def generate_response(request: ChatRequest):
    try:
        if not rails:
            raise HTTPException(status_code=500, detail="Server not ready")
        logger.info(f"User: {request.query}")
        messages = [{"role": "user", "content": request.query}]
        async_response = rails.stream_async(messages)
        logger.info(f"Bot: {async_response}")

        return StreamingResponse(
            async_response,
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)