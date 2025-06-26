# How to Run the Ryan Bot Example

## 1. create python virtual environment
```
python3 -m venv venv
```

## 2. activate/deactivate python virtual environment
```
source venv/bin/activate
deactivate
```

## 3. [install nemoguardrails](https://docs.nvidia.com/nemo/guardrails/latest/getting-started/installation-guide.html)
```
# pip install nemoguardrails
# pip install nemoguardrails[all]
```

## 4. clone nemoguardrails repository
```
git clone https://github.com/NVIDIA/NeMo-Guardrails.git
cd nemo-guardrails
```

## 5. install dependencies
```
pip install -e .

# loading model dependencies
cd ./rya-bot
pip install -r requirements.txt
```

## 6. launch nemoguardrails server
- If you enable chat-ui, you can use the following command:
```
cd ./ryan-bot
nemoguardrails server --config=./config
```

- If you disable chat-ui, you can use the following command:
```
# launch server without chat-ui (please check the path of the config file)
nemoguardrails server --config=./config --disable-chat-ui --default-config-id=default

# launch client
cd ryan-bot/ryan-client
python ryan_dmeo_client.py  # recommend
or
python restful_api_client.py
```

## 7. login to nemoguardrails server
```
http://localhost:8000

## Caution
Pay attentation to the path of current module, if you are not in the root directory of NeMo-Guardrails, you should use the absolute path in config.yml
```