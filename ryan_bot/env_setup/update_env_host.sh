#!/bin/bash

# 更新.env.ryan_niu文件中的HOST值
curr_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ENV_FILE=$curr_dir/.env.$USER
echo "machine name: $USER@$HOSTNAME"
echo "env file: $ENV_FILE"

# 检查当前用户是否为ryan_niu且主机名不是gn403
if [ "$USER" != "ryan_niu" ] && [ "$HOSTNAME" != "gn403" ]; then
    echo "当前用户不是ryan_niu, 且hostname不是gn403时, 脚本终止"
    exit 0
fi

# 获取当前主机的IP地址（排除127.0.0.1）
NEW_HOST=$(nslookup $HOSTNAME | grep -oP 'Address:\s*\K(?!127\.0\.)[\d\.]+')

# 检查是否成功获取IP
if [ -z "$NEW_HOST" ]; then
    echo "无法获取主机IP地址"
    exit 1
fi

# 使用sed命令替换HOST行
sed -i "s/^HOST=.*/HOST=$NEW_HOST/" "$ENV_FILE"
echo "已将.env.ryan_niu中的HOST更新为: $NEW_HOST"