#!/bin/bash

select_env_file() {
    # Step 1: 导出环境变量供其他脚本使用
    echo -e "\n当前的工作路径为: $PWD"
    if [ "$(whoami)" = "ubuntu" ]; then
        # export LLM_DIR="/home/ubuntu/workspace/llm"
        # export MODEL_NAME="Qwen2_BE_0.6B"
        # export ENGINE_NAME="ryan_local_engine"
        echo "import env from .env.ubuntu file"
    elif [ "$(whoami)" = "root" ]; then
        # export LLM_DIR="/root/ryan/llm"
        # export MODEL_NAME="Qwen2.5-7B-Instruct"
        # # export ENGINE_NAME="ryan_vllm_engine"
        # export ENGINE_NAME="ryan_local_engine"

        echo "import env from .env.root file"
    elif [ "$(whoami)" = "ryan_niu" ]; then
        # export LLM_DIR="/home/ryan_niu/ryan/llm"
        # export MODEL_NAME="Qwen2.5-7B-Instruct"
        # export ENGINE_NAME="ryan_vllm_engine"
        # export ENGINE_NAME="ryan_local_engine"
        echo "import env from .env.ryan_niu file"
    else
        echo "ERROR!!! Please check the current SYSTEM USER"
        exit 1
    fi

    read -p "请输入当前环境的llm文件夹路径 [默认: $LLM_DIR]: " current_llm_dir

    # 如果用户输入不为空，则更新LLM_DIR
    [ -n "$current_llm_dir" ] && export LLM_DIR="$current_llm_dir"
}

activate_python_env() {
    # Step 3: 创建并激活python虚拟环境
    apt install python3-venv -y && python3 -m venv venv && source venv/bin/activate
    # apt install python3-venv -y && python3 -m venv ~/my_venv_312 && source ~/my_venv_312/bin/activate
}