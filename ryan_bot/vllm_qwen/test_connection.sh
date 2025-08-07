#!/bin/bash

curl http://10.16.116.100:8010/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello! What is vLLM?"}]
  }'