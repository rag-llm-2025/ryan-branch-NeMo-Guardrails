#!/usr/bin/env bash

set -ex

# # Step 1: 检查是否在虚拟环境中
# if [ -z "$VIRTUAL_ENV" ]; then
#     echo "警告：当前不在Python虚拟环境中执行！"
#     echo "请先激活虚拟环境：source venv/bin/activate"
#     exit 1
# fi

# Step 2: 设置日志目录
DATESTR=$(date +%Y%m%d-%H%M%S)
LOG_DIR="logs"
mkdir -p $LOG_DIR
LOG_FILE="${LOG_DIR}/client_${DATESTR}.log"
LLM_DIR=${1:-"/root/ryan/llm"}


# Step 3: 启动客户端
echo "正在启动客户端..."
# If you want to launch client in the docker
cd $LLM_DIR/src/nemo-guardrails
python ./ryan_bot/ryan-client/ryan_demo_client.py --server-url http://localhost:8000 --api-key $API_KEY --api-secret $API_SECRET 2>&1 | tee $LOG_FILE

# If you want to launch client in the local browser with VScode
# http://localhost:8000

echo "客户端退出，日志保存在: $LOG_FILE"

# Step 4: 退出虚拟环境
# deactivate