from fastapi import FastAPI, Request
from nemoguardrails import LLMRails, RailsConfig
import os
import time
from nemoguardrails.ryan_logger import ryan_log

config_path = os.getenv("GUARDRAILS_CONFIG_ID", "./")
config = RailsConfig.from_path(config_path)
rails = LLMRails(config)

app = FastAPI()

@app.post("/generate")
async def generate(request: Request):

    start_time = time.time()
    data = await request.json()
    ryan_log.critical(f"received request: {data}")
    user_id = data.get("user_id")
    user_query = data.get("query")

    response = await rails.generate_async(prompt=user_query)
    time_cost = (time.time() - start_time) * 1000
    ryan_log.critical(f"time cost: {time_cost}ms")

    return {"user_id": user_id, "reply": response}
