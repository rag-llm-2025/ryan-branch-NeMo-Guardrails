#!/usr/bin/env bash

# set -ex

# load .env and set environment variables first
export USER=$(whoami)
source ./env_setup/.env.$(whoami)

WORKESPACE=../
RYAN_BOT=./ryan_bot

# install dependencies
install_dependencies() {
    cd $WORKESPACE && pip install -e .
    cd $RYAN_BOT && pip install -r requirements.txt
}

install_dependencies

# check CUDA availability
check_cuda_and_run() {
    if command -v nvidia-smi &> /dev/null && \
       command -v nvcc &> /dev/null && \
       python3 -c "import torch; print(torch.cuda.is_available())" | grep -q 'True'; then
        echo "CUDA is available. Displaying GPU information:"
        nvidia-smi
        echo "Setting device to cuda"
        export DEVICE="cuda"
    else
        echo "CUDA is not available. Using CPU."
        export DEVICE="cpu"
    fi
}
check_cuda_and_run

# check env
cd $WORKESPACE && python3 -c "import nemoguardrails; print(nemoguardrails.__version__)"
