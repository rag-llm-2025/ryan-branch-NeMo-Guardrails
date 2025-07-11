#!/usr/bin/env bash

# 参数默认值
INSTALL=false
UPDATE_YAML=false
HELP=false

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  --install=true|false     是否安装依赖 (默认: false)"
    echo "  --update-yaml=true|false 是否更新YAML配置 (默认: false)"
    echo "  --help, -h              显示帮助信息"
}

# 参数解析函数
parse_params() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --install=*|install=*)
                INSTALL="${1#*=}"
                shift
                ;;
            --update-yaml=*|update-yaml=*)
                UPDATE_YAML="${1#*=}"
                shift
                ;;
            --help|-h)
                HELP=true
                shift
                ;;
            *)
                echo "未知参数: $1"
                exit 1
                ;;
        esac
    done
}
parse_params "$@"

echo -e "***************************************************************************"
echo -e "Input Params:"
echo -e "install:       $INSTALL"
echo -e "update_yaml:   $UPDATE_YAML"
echo -e "***************************************************************************"
# read -p "Press Enter to continue..."