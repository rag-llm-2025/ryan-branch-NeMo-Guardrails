#!/bin/bash

# python -m vllm.entrypoints.api_server \
#   --model Qwen/Qwen2.5-7B-Instruct \
#   --host 10.16.118.42 \
#   --port 8010 \
#   --tensor-parallel-size 1

HOST=${HOST:-localhost}
PORT=${PORT:-8010}

echo "HOST: ${HOST}"
echo "PORT: ${PORT}"

vllm serve Qwen/Qwen2.5-7B-Instruct \
    --host ${HOST} \
    --port ${PORT} \
    --tensor-parallel-size 1