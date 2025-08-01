#!/bin/bash

HOST=${HOST:-localhost}
PORT=${PORT:-8080}

uvicorn server:app --host $HOST --port $PORT