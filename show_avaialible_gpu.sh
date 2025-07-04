#!/bin/bash

# 定义函数，用于获取指定分区的GPU架构
get_gpu_arch() {
    local partition_name=$1
    local gpu_arch=""

    # 获取指定分区的信息
    partition_info=$(scontrol show partition $partition_name)

    # 提取Gres中的GPU架构信息
    gpu_arch=$(echo "$partition_info" | grep "TRES=" | grep -oP "(?<=gres/gpu:)[^=]+")

    echo "$gpu_arch"
}

# 定义一个函数来获取节点的 GPU 信息
get_gpu_info() {
    local node=$1
    local gpu_arch=$2
    # 获取节点总内存和剩余内存
    total_mem=$(scontrol show node "$node" | grep -o "RealMemory=[0-9]*" | awk -F'=' '{print $2}' | grep -o '[0-9]*')
    free_mem=$(scontrol show node "$node" | grep -o "FreeMem=[0-9]*" | awk -F'=' '{print $2}' | grep -o '[0-9]*')
    free_mem_gb=$((free_mem / 1024))
    total_mem_gb=$((total_mem / 1024))
    # 获取配置的GPU数量
    cfg_gpu=$(scontrol show node "$node" | grep "CfgTRES" | grep -o "gpu:${gpu_arch}=[0-9]*" | awk -F'=' '{print $2}' | grep -o '[0-9]*')
    # 获取节点IP地址
    ip=$(nslookup "$node" | grep -oP 'Address:\s*\K(?!127\.0\.)[\d\.]+')

    node_state=$(scontrol show node "$node" | grep "State=" | awk -F= '{print $2}' | awk '{print $1}')
    if [[ "$node_state" == "IDLE" || "$node_state" == "MIXED" ]]; then
        # 获取已分配的GPU数量
        alloc_gpu=$(scontrol show node "$node" | grep "AllocTRES" | grep -o "gpu:${gpu_arch}=[0-9]*" | awk -F'=' '{print $2}' | grep -o '[0-9]*')

        cfg_gpu=${cfg_gpu:-0} # 如果未设置，则默认为0
        alloc_gpu=${alloc_gpu:-0}

        # 返回一个包含两个元素的数组：总GPU数量,可用GPU数量,剩余内存
        echo "$cfg_gpu $((cfg_gpu - alloc_gpu)) ${free_mem_gb} ${total_mem_gb} $ip"
    else
        echo "$cfg_gpu 0 ${free_mem_gb} ${total_mem_gb} $ip"
    fi
}

# 定义一个函数输出分区信息
get_partition_gpu_info() {
    # 获取该分区上的所有节点
    nodes=$(sinfo -p "$1" -N -h -o "%N")
    if [ -z "$nodes" ]; then
        echo "Error: $1 isn't a valid partition name, please check with 'sinfo'"
        return
    fi
    # 获取该分区的GPU架构
    gpu_arch=$(get_gpu_arch "$1")
    if [ -z "$gpu_arch" ]; then
        echo "Partition $1 doesn't have any gpus"
        return
    fi
    
    total_gpus=0
    available_gpus=0
    free_mems=0
    total_mems=0
    for node in $nodes; do
        node_info=$(get_gpu_info "$node" "$gpu_arch")
        node_cfg_gpu=$(echo $node_info | awk '{print $1}')
        node_available_gpu=$(echo $node_info | awk '{print $2}')
	node_free_mem=$(echo $node_info | awk '{print $3}')
	node_total_mem=$(echo $node_info | awk '{print $4}')
	node_ip=$(echo $node_info | awk '{print $5}')
        #echo "Node $node: Total $gpu_arch GPUs: $node_cfg_gpu, Available: $node_available_gpu, Free Memory: $node_free_mem GB, Total Memory: $node_total_mem GB, IP Address: $node_ip"
	printf "Node %-6s: Total %-6s GPUs: %-2d, Available: %-2d, Free Memory: %-4d GB, Total Memory: %-4d GB, IP Address: %s\n" \
    "$node" "$gpu_arch" "$node_cfg_gpu" "$node_available_gpu" "$node_free_mem" "$node_total_mem" "$node_ip"

        total_gpus=$((total_gpus + node_cfg_gpu))
        available_gpus=$((available_gpus + node_available_gpu))
	free_mems=$((free_mems + node_free_mem))
	total_mems=$((total_mems + node_total_mem))
    done
    echo "Partition $1 Total $gpu_arch GPUs: $total_gpus, Available: $available_gpus, Free Memory: $free_mems GB, Total Memory: $total_mems GB"
}

process_partitions() {
    local key="$1"

    if [ -n "${partition_dict[$key]}" ]; then
        local partitions="${partition_dict[$key]}"

        # 循环遍历所有分区并调用函数
        for partition in $partitions; do
            get_partition_gpu_info "$partition"
        done
    else
        get_partition_gpu_info "$key"
    fi
}

# 自定义group
declare -A partition_dict
partition_dict=(
    [a100]="a100.80gb a100.40gb a100.pci"
    [v100]="v100"
    [h100]="h100.80gb"
    [h200]="h200.141gb"
    [t4]="cpu cpu.t4 cpu.t4.cuda12"
    [all]="a100.80gb a100.40gb a100.pci v100 h100.80gb h200.141gb cpu cpu.t4 cpu.t4.cuda12 gpu gcpu"
)

# 检查是否提供了参数
if [ -z "$1" ]; then
    echo "Error: Please provide a partition or group name as an argument. Use --help to see available options."
    exit 1
fi

if [ "$1" == "--help" ]; then
    echo "Available groups:"
    for key in "${!partition_dict[@]}"; do
        echo "  $key"
    done

    echo -e "\nAvailable partitions:"
    sinfo -h -o "%P" | grep -v "^PARTITION" | sort | uniq | sed 's/^/  /'
    exit 0
fi

process_partitions "$1"
