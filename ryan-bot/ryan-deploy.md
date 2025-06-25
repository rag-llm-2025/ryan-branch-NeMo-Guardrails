# How to Run the Ryan Bot Example

## 1. create python virtual environment
python3 -m venv venv

## 2. activate python virtual environment
source venv/bin/activate

## 3. [install nemoguardrails](https://docs.nvidia.com/nemo/guardrails/latest/getting-started/installation-guide.html)
pip install nemoguardrails
pip install nemoguardrails[all]

## 4. clone nemoguardrails repository
git clone https://github.com/NVIDIA/NeMo-Guardrails.git
cd nemo-guardrails

## 5. install dependencies
pip install -e .

## 6. launch nemoguardrails server
- If you enable chat-ui, you can use the following command:
```
cd ./ryan-bot
nemoguardrails server --config=./config
```

- If you disable chat-ui, you can use the following command:
```
# 启动服务器(确保使用正确的config目录路径)
nemoguardrails server --config=./config --disable-chat-ui --default-config-id=default

# 启动client
cd ryan-bot/ryan-client
python ryan_dmeo_client.py
or
python restful_api_client.py
```

## 7. login to nemoguardrails server
http://localhost:8000

## Caution
Pay attentation to the path of current module, if you are not in the root directory of NeMo-Guardrails, you should use the absolute path in config.yml