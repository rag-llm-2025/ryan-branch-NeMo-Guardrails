#!/bin/bash

# export HOST=gn401.crg.cerence.net
# export PORT=8010
# export OPENAI_API_KEY=sk-xxx
# export OPENAI_BASE_URL=http://${HOST}:${PORT}/v1
# export OPENAI_URL_AUTH="6exxxxAv"


HOST=${HOST:-localhost}
PORT=${PORT:-8010}

echo "HOST: ${HOST}"
echo "PORT: ${PORT}"

python ./demo.py --host ${HOST} --port ${PORT}