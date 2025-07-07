#!/bin/bash

# parameter check
if [ $# -eq 0 ]; then
    echo "Error! Please check the input params, eg.: ./replace_engine.sh ryan_vllm_engine  ~/ryan/llm"
    exit 1
fi

# do replacement directly in the source file
sed -i "s/ryan_.*_engine/$1/g" "$2/src/nemo-guardrails/ryan_bot/config/qwen_model/prompts/ryan_qwen2.yml"

echo "Done! Already replaced ryan_.*_engine to $1"