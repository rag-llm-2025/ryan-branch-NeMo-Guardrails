## 检查服务是否运行
ps aux | grep vllm

## 或者测试API端点是否可达
curl http://gn402.crg.cerence.net:8010/v1/models

## 检查网络连接是否正常：
```
ping gn402.crg.cerence.net
telnet gn402.crg.cerence.net 8010
nslook gn402.crg.cerence.net
```

## 检查vLLM服务日志，确认是否有错误：
```
journalctl -u vllm --no-pager -n 50
```

# 创建/激活conda环境
conda create -n vllm_qwen python=3.12
conda activate vllm_qwen

# 环境变量
```
export HOST=10.16.118.41
export PORT=8010
export OPENAI_API_KEY=sk-xxx
export OPENAI_BASE_URL=http://${HOST}:${PORT}/v1
export OPENAI_URL_AUTH=6e-xxxxy-Av
```

# 启动服务
cd ryan_bot
./server_vllm_runner.sh --host ${HOST} --port ${PORT}

# 启动客户端
./client_vllm_runner.sh --host ${HOST} --port ${PORT}
OR
python ./demo.py --host ${HOST} --port ${PORT}

# gpt-4o拦截效果摸底测试
```
python gpt_4o_verify.py --type classification --mode interactive
python gpt_4o_verify.py --type generation --mode interactive

python gpt_4o_verify.py --type classification --mode batch --input data/user_messages.jsonl --output ./output/test_gpt_4o_classification.txt

python gpt_4o_verify.py --type generation --mode batch --input data/user_messages.jsonl --output ./output/test_gpt_4o_generation.txt
```