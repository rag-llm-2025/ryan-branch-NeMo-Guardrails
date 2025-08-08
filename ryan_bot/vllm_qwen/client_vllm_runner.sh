#!/bin/bash

VLLM_HOST=${VLLM_HOST:-localhost}
PORT=${PORT:-8010}

echo "VLLM_HOST: ${VLLM_HOST}"
echo "PORT: ${PORT}"

python ./demo.py --host ${VLLM_HOST} --port ${PORT}