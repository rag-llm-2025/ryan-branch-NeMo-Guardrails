#!/usr/bin/env bash

set -ex

# config params
WORK_DIR="/home/ubuntu/workspace/llm" # ls: models src
export MODEL_NAME="Qwen2_BE_0.6B"
export MODEL_PATH="$WORK_DIR/models/$MODEL_NAME"
export CHECKPOINT_PATH="$WORK_DIR/src/qwen2-fine-tuning/qwen2/output/hotel_qwen2-ryan-test-20250611/checkpoint-8000"
export DEVICE="cpu"  # cuda或 cpu
export YML_CONFIG_PATH="./config"
export UPDATE_CONFIG="true"

# define function to check if cuda is available
check_cuda_and_run() {
    if command -v nvidia-smi &> /dev/null; then
        echo "CUDA is available. Displaying GPU information:"
        nvidia-smi
        echo "Running run_guardrails_server.py on GPU 0..."
        DEVICE="cuda" # set device to cuda
    else
        echo "CUDA is not available. Please check your installation."
        DEVICE="cpu" # set device to cpu
    fi
}

run_guardrails_server() {
    # set log dir and log file
    DATESTR=`date +%Y%m%d-%H%M%S`
    LOG_DIR="logs"
    mkdir -p $LOG_DIR
    LOG_FILE="${LOG_DIR}/demo_${DATESTR}.log"

    # 先更新config.yml文件
    python3 -c "from utils.helper import yml_config_update; yml_config_update('$YML_CONFIG_PATH', '$MODEL_NAME', '$MODEL_PATH', '$DEVICE', '$CHECKPOINT_PATH')"

    # 然后启动server
    nemoguardrails server --config=./config 2>&1 | tee $LOG_FILE
}

# call function to check if cuda is available
# check_cuda_and_run

# call function to run demo.py
run_guardrails_server

echo "Demo Done, log saved to: $LOG_FILE"