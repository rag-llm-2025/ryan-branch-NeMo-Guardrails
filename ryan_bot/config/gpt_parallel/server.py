from fastapi import FastAPI, Request
from nemoguardrails import LLMRails, RailsConfig

# 初始化Guardrails配置（假设已定义规则）
config = RailsConfig.from_path("./")  # 包含guardrails规则的文件夹
rails = LLMRails(config)

app = FastAPI()

@app.post("/generate")
async def generate(request: Request):
    # 接收客户端请求，包含user_id和用户指令
    data = await request.json()
    user_id = data.get("user_id")  # 用户唯一标识
    user_query = data.get("query")  # 用户指令

    # 调用Nemo Guardrails处理请求（异步处理，支持并发）
    response = await rails.generate_async(prompt=user_query)

    # 返回结果时携带user_id，供客户端匹配
    return {
        "user_id": user_id,
        "reply": response
    }

# 启动服务：uvicorn main:app --host 0.0.0.0 --port 8000
