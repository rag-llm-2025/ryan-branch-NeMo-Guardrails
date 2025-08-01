#!/bin/bash

curl http://10.16.118.42:8010/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello! What is vLLM?"}]
  }'
