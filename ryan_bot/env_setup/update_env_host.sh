#!/bin/bash

# 更新.env.ryan_niu文件中的HOST值
curr_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ENV_FILE=$curr_dir/.env.$(whoami)
echo "machine name: $(whoami)@$HOSTNAME"
echo "env file: $ENV_FILE"

# 获取当前主机的IP地址（排除127.0.0.1）
NEW_HOST=$(nslookup $HOSTNAME | grep -oP 'Address:\s*\K(?!127\.0\.)[\d\.]+')

# 检查是否成功获取IP
if [ -z "$NEW_HOST" ]; then
    echo "无法获取主机IP地址"
    exit 1
fi

# 检查当前用户是为ryan_niu且主机名是gn403
if [ "$(whoami)" == "ryan_niu" ] && [ "$HOSTNAME" == "gn403" ]; then
    echo "当前用户是ryan_niu, 且hostname是gn403时, 替换HOST为: $NEW_HOST"
    # 使用sed命令替换HOST行
    sed -i "s/^HOST=.*/HOST=$NEW_HOST/" "$ENV_FILE"
    echo "已将.env.ryan_niu中的HOST更新为: $NEW_HOST"
fi
