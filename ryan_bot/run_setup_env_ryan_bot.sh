#!/usr/bin/env bash

# Description:
# cmd: ./run_setup_env_ryan_bot.sh install=true update_yaml=true

# set -ex

# parse params
source "$(dirname "${BASH_SOURCE[0]}")/include.sh"

# show help info: ./run_setup_env_ryan_bot.sh -h/--help
if [ "$HELP" = true ]; then
    show_help
    exit 0
fi

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

# load .env and set environment variables first
curr_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo "curr_dir: $curr_dir"
source $curr_dir/env_setup/check_env_config.sh


install_dependencies() {
    # Step 4: 在虚拟环境安装依赖
    cd $LLM_DIR/src/nemo-guardrails/ && pip install -e .
    cd $LLM_DIR/src/nemo-guardrails/ryan_bot/ && pip install -r requirements.txt
}
if [ "$INSTALL" = "true" ]; then
    install_dependencies
else
    echo "skip dependencies installation"
fi


# Step 2: 检查CUDA可用性并更新device
check_cuda_and_run() {
    # 检查CUDA驱动和运行时是否可用
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

# Step 5:更新yml配置文件
update_yaml() {
    export YML_CONFIG_PATH="./config/qwen_model/config.yml" # 注意修改的是QWen模型的yml文件
    cd $LLM_DIR/src/nemo-guardrails/ryan_bot/ && python3 -c "from utils.helper import yml_config_update; yml_config_update('$YML_CONFIG_PATH', '$ENGINE_NAME', '$MODEL_NAME', '$MODEL_PATH', '$DEVICE', '$CHECKPOINT_PATH')"
}

if [ "$UPDATE_YAML" = "true" ]; then
    update_yaml
else
    echo "skip update yml config in shell script"
fi

# Step 6: 在虚拟环境测试运行环境
cd $LLM_DIR/src/nemo-guardrails/ryan_bot/ && python3 -c "import nemoguardrails; print(nemoguardrails.__version__)"
cd $LLM_DIR/src/nemo-guardrails
