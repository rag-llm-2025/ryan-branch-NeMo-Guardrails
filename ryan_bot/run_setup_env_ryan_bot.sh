#!/usr/bin/env bash

set -ex

# 检查是否只导入环境变量
ONLY_EXPORT=${1:-false}

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

# Step 1: 导出环境变量供其他脚本使用
echo -e "\n当前的工作路径为: $PWD"
if [ "$(whoami)" = "ubuntu" ]; then
    export LLM_DIR="/home/ubuntu/workspace/llm"
    export MODEL_NAME="Qwen2_BE_0.6B"
    export ENGINE_NAME="ryan_local_engine"
elif [ "$(whoami)" = "root" ]; then
    export LLM_DIR="/root/ryan/llm"
    export MODEL_NAME="Qwen2.5-7B-Instruct"
    # export ENGINE_NAME="ryan_vllm_engine"
    export ENGINE_NAME="ryan_local_engine"
else
    export LLM_DIR="/home/ubuntu/workspace/llm"
    export MODEL_NAME="Qwen2_BE_0.6B"
    export ENGINE_NAME="ryan_local_engine"
fi
read -p "请输入当前环境的llm文件夹路径 [默认: $LLM_DIR]: " current_llm_dir

# 如果用户输入不为空，则更新LLM_DIR
[ -n "$current_llm_dir" ] && export LLM_DIR="$current_llm_dir"

export MODEL_PATH="$LLM_DIR/models/$MODEL_NAME"
export CHECKPOINT_PATH=""
export DEVICE="cpu"  # 默认值，会被下面的检查覆盖
export YML_CONFIG_PATH="./config/qwen_model/config.yml" # 注意修改的是QWen模型的yml文件

# 如果只导入环境变量，则退出
if [ "$ONLY_EXPORT" = "true" ]; then
    echo "只导出环境变量，跳过后续步骤"
    exit 0
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
echo -e "\n============================================================"
echo "当前环境变量："
echo "engine_name=$ENGINE_NAME"
echo "model_name=$MODEL_NAME"
echo "model_path=$MODEL_PATH, device=$DEVICE"
echo -e "============================================================\n"
read -p "请确认是否使用 $DEVICE 设备 [y/n]: " confirm


# Step 3: 创建并激活python虚拟环境
sudo apt install python3-venv -y && python3 -m venv venv && source venv/bin/activate

# Step 4: 在虚拟环境安装依赖
cd $LLM_DIR/src/nemo-guardrails/ && pip install -e .
cd $LLM_DIR/src/nemo-guardrails/ryan_bot/ && pip install -r requirements.txt


# Step 5:更新yml配置文件
update_config() {
    python3 -c "from utils.helper import yml_config_update; yml_config_update('$YML_CONFIG_PATH', '$ENGINE_NAME', '$MODEL_NAME', '$MODEL_PATH', '$DEVICE', '$CHECKPOINT_PATH')"
}
update_config

# Step 6: 在虚拟环境测试运行环境
cd $LLM_DIR/src/nemo-guardrails/ryan_bot/ && python3 -c "import nemoguardrails; print(nemoguardrails.__version__)"
cd $LLM_DIR/src/nemo-guardrails
