#!/usr/bin/env bash

# set -ex

# Step 1: 检查是否在虚拟环境中
# if [ -z "$VIRTUAL_ENV" ]; then
#     echo "警告：当前不在Python虚拟环境中执行！"
#     echo "请先激活虚拟环境：source venv/bin/activate"
#     exit 1
# fi

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

# If you disable chat-ui, you can use the following command:
nemoguardrails server --config=./ryan_bot/config --disable-chat-ui --default-config-id=qwen_model --host ${HOST} --port ${PORT} --verbose 2>&1 | tee $LOG_FILE

echo "服务端退出，日志保存在: $LOG_FILE"

# Step 4: 退出虚拟环境
# deactivate