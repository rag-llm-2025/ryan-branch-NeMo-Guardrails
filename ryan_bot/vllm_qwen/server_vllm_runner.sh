#!/bin/bash

# python -m vllm.entrypoints.api_server \
#   --model Qwen/Qwen2.5-7B-Instruct \
#   --host 10.16.118.42 \
#   --port 8010 \
#   --tensor-parallel-size 1

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8010}

echo "HOST: ${HOST}"
echo "PORT: ${PORT}"

vllm serve Qwen/Qwen2.5-7B-Instruct \
    --port ${PORT} \
    --tensor-parallel-size 1