# How to Run the Ryan Bot Example

## 1. clone nemoguardrails repository
```
git clone https://github.com/NVIDIA/NeMo-Guardrails.git -b ryan-qwen-demo
```
## 2. setup running environment
```
conda create -n vllm_qwen python=3.12
conda activate vllm_qwen

cd ryan_bot/
source ./ryan_bot/run_setup_env_ryan_bot.sh
```

## 3. run the server in python virtual environment
```
cd ryan_bot/vllm_qwen
./server_vllm_runner.sh
```

## 4. run the client in python virtual environment
```
cd ryan_bot/vllm_qwen
./client_vllm_runner.sh
```






## 5. launch nemoguardrails server
- If you enable chat-ui, you can use the following command:
```
cd ./ryan_bot
nemoguardrails server --config=./config --default-config-id=qwen_model
```

- If you disable chat-ui, you can use the following command:
```
# launch server without chat-ui (please check the path of the config file)
nemoguardrails server --config=./config --disable-chat-ui --default-config-id=qwen_model

# launch client
cd ryan_bot/ryan-client
python ryan_dmeo_client.py  # recommend
or
python restful_api_client.py
```

## 6. connect to server via chat-ui client
```
http://localhost:8000
```

## 7. VScode Debug in Docker
```
cd nemo-guardrails
select and start debug configuration -> Debug Ryan Bot Server
F5 -> launch server

cd nemo-guardrails/ryan_bot
python ryan_dmeo_client.py  # launch client to start the conversation
```

# Reference
- [install nemoguardrails](https://docs.nvidia.com/nemo/guardrails/latest/getting-started/installation-guide.html)
```
# pip install nemoguardrails
# pip install nemoguardrails[all]
```