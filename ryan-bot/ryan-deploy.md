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
cd ./ryan-bot
nemoguardrails server --config=./config

## 7. login to nemoguardrails server
http://localhost:8000

## Caution
Pay attentation to the path of current module, if you are not in the root directory of NeMo-Guardrails, you should use the absolute path in config.yml