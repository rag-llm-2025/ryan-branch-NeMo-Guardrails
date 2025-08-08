from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from nemoguardrails import LLMRails, RailsConfig
from contextlib import asynccontextmanager
from nemoguardrails.logging.verbose import console

from simple_logger import RyanLogger as logger

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

class ChatRequest(BaseModel):
    user_id: str
    query: str

@app.post("/generate")
async def generate_response(request: ChatRequest):
    try:
        if not rails:
            raise HTTPException(status_code=500, detail="Server not ready")
        logger.info(f"User: {request.query}")
        response = await rails.generate_async(request.query)
        logger.info(f"Bot: {response}")
        return {request.user_id: response}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)