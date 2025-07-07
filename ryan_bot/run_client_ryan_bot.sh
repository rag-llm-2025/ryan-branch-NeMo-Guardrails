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
rm -f $LOG_DIR/ryan_client_*.log
LOG_FILE="${LOG_DIR}/ryan_client_${DATESTR}.log"

echo -e "\n当前的工作路径为: $PWD"
if [ "$(whoami)" = "ubuntu" ]; then
    export LLM_DIR="/home/ubuntu/workspace/llm"
elif [ "$(whoami)" = "root" ]; then
    export LLM_DIR="/root/ryan/llm"
elif [ "$(whoami)" = "ryan_niu" ]; then
    export LLM_DIR="/home/ryan_niu/ryan/llm"
else
    export LLM_DIR="/home/$(whoami)/llm"  # 其他用户默认路径
fi
# read -p "当前环境的llm路径: $LLM_DIR"

# LLM_DIR=${1:-"/root/ryan/llm"}


# Step 3: 启动客户端
echo "正在启动客户端..."
# If you want to launch client in the docker
cd $LLM_DIR/src/nemo-guardrails

# 在环境变量设置部分添加（与服务端脚本一致）
# 在环境变量设置部分添加（与客户端脚本一致）
if [ "$(whoami)" = "ryan_niu" ]; then
    # srun --partition=h100.80gb --gres=gpu:hopper:1 --nodelist=gn403 --mem=30G --job-name=ryan_sever  --pty bash -i
    export SERVER_IP="10.16.118.43" # ifconfig

    # srun --partition=a100.40gb --gres=gpu:ampere:1 --nodelist=gn201 --mem=30G --job-name=ryan_sever  --pty bash -i
    # export SERVER_IP="10.16.118.11" # ifconfig
else
    export SERVER_IP="0.0.0.0"
fi

export API_KEY="test_key"
export API_SECRET="test_secret"
python3 ./ryan_bot/ryan-client/ryan_demo_client.py --server-url http://${SERVER_IP}:8000 --api-key $API_KEY --api-secret $API_SECRET 2>&1 | tee $LOG_FILE

# If you want to launch client in the local browser with VScode
# http://localhost:8000

echo "客户端退出，日志保存在: $LOG_FILE"

# Step 4: 退出虚拟环境
# deactivate