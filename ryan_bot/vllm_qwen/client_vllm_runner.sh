#!/bin/bash

HOST=${HOST:-localhost}
PORT=${PORT:-8010}

echo "HOST: ${HOST}"
echo "PORT: ${PORT}"

python ./demo.py --host ${HOST} --port ${PORT}