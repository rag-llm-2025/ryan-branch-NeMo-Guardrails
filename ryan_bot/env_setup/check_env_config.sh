#!/bin/bash

# 打印分隔线
function print_separator() {
    echo "----------------------------------------"
}

# 打印带颜色的标题
function print_header() {
    echo -e "\033[1;36m$1\033[0m"  # 青色加粗
}

# 打印键值对
function print_kv() {
    printf "%-20s: %s\n" "$1" "${!1:-未设置}"
}

# get current directory
curr_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# update ryan_niu@gn403 host ip based on current cluster server
source $curr_dir/update_env_host.sh

# load .env config
source $curr_dir/.env.$(whoami)
print_header "当前环境变量文件"
printf "%-20s: %s\n" "$curr_dir/.env.$(whoami)"
print_separator

# 1. 网络相关配置
print_header "网络配置"
print_kv "HOST"
print_kv "PORT"
print_separator

# 2. API认证配置
print_header "API认证配置"
print_kv "API_KEY"
print_kv "API_SECRET"
print_separator

# 3. 开发调试配置
print_header "开发调试配置"
print_kv "DEBUG"
print_kv "PRJ_ENV"
print_kv "LOGGER_LEVEL"
print_separator

# 4. NeMo Guardrails配置
print_header "NeMo Guardrails配置"
print_kv "LLM_DIR"
print_kv "MODEL_NAME"
print_kv "ENGINE_NAME"
print_separator