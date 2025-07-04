#!/usr/bin/env bash

# set -ex

# Step 1: 检查是否在虚拟环境中
# if [ -z "$VIRTUAL_ENV" ]; then
#     echo "警告：当前不在Python虚拟环境中执行！"
#     echo "请先激活虚拟环境：source venv/bin/activate"
#     exit 1
# fi

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
elif [ "$(whoami)" = "ryan_niu" ]; then
    export LLM_DIR="/home/ryan_niu/ryan/llm"
    export MODEL_NAME="Qwen2.5-7B-Instruct"
    # export ENGINE_NAME="ryan_vllm_engine"
    export ENGINE_NAME="ryan_local_engine"
else
    export LLM_DIR="/home/ubuntu/workspace/llm"
    export MODEL_NAME="Qwen2_BE_0.6B"
    export ENGINE_NAME="ryan_local_engine"
fi
# read -p "当前环境的llm路径: $LLM_DIR"

# LLM_DIR=${1:-"/root/ryan/llm"}


# Step 2: 设置日志目录
DATESTR=$(date +%Y%m%d-%H%M%S)
LOG_DIR="logs"
mkdir -p $LOG_DIR
rm -f $LOG_DIR/ryan_server_*.log
LOG_FILE="${LOG_DIR}/ryan_server_${DATESTR}.log"

# Step 3: 启动服务器
echo "正在启动服务器..."
cd $LLM_DIR/src/nemo-guardrails/
# If you want to enable chat-ui, you can use the following command:
# nemoguardrails server --config=./ryan_bot/config --default-config-id=qwen_model --verbose 2>&1 | tee $LOG_FILE
# nemoguardrails server --config=./ryan_bot/config/qwen_model --verbose 2>&1 | tee $LOG_FILE

# 在环境变量设置部分添加（与客户端脚本一致）
if [ "$(whoami)" = "ryan_niu" ]; then
    export SERVER_IP="10.16.118.43" # ifconfig
else
    export SERVER_IP="0.0.0.0"
fi

# If you disable chat-ui, you can use the following command:
nemoguardrails server --config=./ryan_bot/config --disable-chat-ui --default-config-id=qwen_model --host ${SERVER_IP} --port 8000 --verbose 2>&1 | tee $LOG_FILE

echo "服务端退出，日志保存在: $LOG_FILE"

# Step 4: 退出虚拟环境
# deactivate