#!/usr/bin/env bash

# Description:
# cmd: ./run_setup_env_ryan_bot.sh install=true update_yaml=true

# set -ex

INSTALL=true

# 打印示例目录结构
echo "示例目录结构："
echo "/home/ubuntu/llm"
echo "├── models"
echo "│   ├── Qwen2_BE_0.6B"
echo "│   └── deepseek"
echo "└── src"
echo "    ├── nemo-guardrails"
echo "        └── config"
echo "            └── qwen_model"
echo "                └── config.yml"

install_dependencies() {
    cd $LLM_DIR/src/nemo-guardrails/ && pip install -e .
    cd $LLM_DIR/src/nemo-guardrails/ryan_bot/ && pip install -r requirements.txt
}
if [ "$INSTALL" = "true" ]; then
    install_dependencies
else
    echo "skip dependencies installation"
fi


check_cuda_and_run() {
    if command -v nvidia-smi &> /dev/null && \
       command -v nvcc &> /dev/null && \
       python3 -c "import torch; print(torch.cuda.is_available())" | grep -q 'True'; then
        echo "CUDA is available. Displaying GPU information:"
        nvidia-smi
        echo "Setting device to cuda"
        export DEVICE="cuda"
    else
        echo "CUDA is not available. Using CPU."
        export DEVICE="cpu"
    fi
}
check_cuda_and_run

update_yaml() {
    export YML_CONFIG_PATH="./config/qwen_model/config.yml"
    cd $LLM_DIR/src/nemo-guardrails/ryan_bot/ && python3 -c "from utils.helper import yml_config_update; yml_config_update('$YML_CONFIG_PATH', '$ENGINE_NAME', '$MODEL_NAME', '$MODEL_PATH', '$DEVICE', '$CHECKPOINT_PATH')"
}

if [ "$UPDATE_YAML" = "true" ]; then
    update_yaml
else
    echo "skip update yml config in shell script"
fi

cd $LLM_DIR/src/nemo-guardrails/ryan_bot/ && python3 -c "import nemoguardrails; print(nemoguardrails.__version__)"
cd $LLM_DIR/src/nemo-guardrails
