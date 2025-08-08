# Topic 1: How to Setup vLLM Server and Guardrail Project

## setup running environment
```
conda create -n vllm_qwen python=3.12
conda activate vllm_qwen

cd ryan_bot/
source ./ryan_bot/run_setup_env_ryan_bot.sh
```

## Create/activate conda environment
conda create -n vllm_qwen python=3.12
conda activate vllm_qwen

## Setup environment variables
```
export VLLM_HOST=gn101.crg.cerence.net
export RAILS_HOST=cn024.crg.cerence.net
export PORT=8010
export OPENAI_API_KEY=sk-xxx
export OPENAI_BASE_URL=http://${HOST}:${PORT}/v1
export OPENAI_URL_AUTH=6e-xxxxy-Av
```

## Lauch server
cd ryan_bot/vllm_qwen
./server_vllm_runner.sh

## Lauch client
./client_vllm_runner.sh
OR
python ./demo.py --host ${HOST} --port ${PORT}

## gpt-4o guardrails Effect Assessment Test
- Test Corpus([Aegis-AI-Content-Safety-Dataset-1.0](https://huggingface.co/datasets/nvidia/Aegis-AI-Content-Safety-Dataset-1.0))
  - Classification Test Corpus：data/user_messages.jsonl
  - Generation Test Corpus：data/user_messages.jsonl
- Test Command
  - Interactive Test
    - Classification Test
    ```
    python gpt_4o_verify.py --type classification --mode interactive
    ```
    - Generation Test
    ```
    python gpt_4o_verify.py --type generation --mode interactive
    ```
  - Batch Test
    - Classification Test
    ```
    python gpt_4o_verify.py --type classification --mode batch --input data/user_messages.jsonl --output ./output/test_gpt_4o_classification.txt
    ```
    - Generation Test
    ```
    python gpt_4o_verify.py --type generation --mode batch --input data/user_messages.jsonl --output ./output/test_gpt_4o_generation.txt
    ```
## FAQ
- check vllm server status
ps aux | grep vllm

- check vllm server api endpoint
curl http://gn402.crg.cerence.net:8010/v1/models

- check network connection
```
ping gn402.crg.cerence.net
telnet gn402.crg.cerence.net 8010
nslook gn402.crg.cerence.net
```

- check vllm server log
```
journalctl -u vllm --no-pager -n 50
```

# Topic 2: Demo Based on vllm Server/Guardrails Project/WebUI Client

- terminal for vllm server(on a100 or h100 gpu)
./server_vllm_runner.sh

- terminal for guardrail project (on tesla t4 or strong cpu)
python api_server.py

- terminal for webui client (on cpu)
python api_client.py