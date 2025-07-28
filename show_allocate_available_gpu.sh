#!/bin/bash
# Description:
# 查看使用帮助： ./show_allocate_available_gpu.sh --help

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

try_allocate() {
    local node=$1
    local partition=$2
    local gres=$3
    local gpu_count=$4
    local mem_gb=$5

    echo "尝试在节点 $node 上申请资源..."
    echo "Debug: Trying to allocate $gpu_count GPU(s) on $node with $mem_gb GB memory"
    echo "Debug: Full command: srun --partition=$partition --gres=$gres:$gpu_count --nodelist=$node --mem=${mem_gb}G --cpus-per-task=8 --job-name=auto_alloc --pty bash -i"
    echo "执行命令: srun --partition=$partition --gres=$gres:$gpu_count --nodelist=$node --mem=${mem_gb}G --cpus-per-task=8 --job-name=auto_alloc --pty bash -i"

    # 实际执行申请命令
    if srun --partition=$partition --gres=$gres:$gpu_count --nodelist=$node --mem=${mem_gb}G --job-name=auto_alloc -c 8 --pty bash -i; then
        echo -e "\033[1;32m资源申请成功！\033[0m"
        return 0
    else
        echo -e "\033[1;31m资源申请失败！\033[0m"
        return 1
    fi
}

# 修改后的主处理函数
process_partitions() {
    local key="$1"
    local auto_allocate=${2:-false}
    local requested_gpus=${3:-1}
    local requested_mem=${4:-30}
    local allocation_success=false
    echo "Debug: Processing GPU type '$key' with partitions: ${partition_dict[$key]}, auto_allocate: $auto_allocate, requested_gpus: $requested_gpus, requested_mem: $requested_mem"

    if [ -n "${partition_dict[$key]}" ]; then
        local partitions="${partition_dict[$key]}"

        for partition in $partitions; do
            get_partition_gpu_info "$partition"

            if [ "$auto_allocate" = true ]; then
                # 获取分区信息
                gpu_arch=$(get_gpu_arch "$partition")
                nodes=$(sinfo -p "$partition" -N -h -o "%N")

                # 尝试在每个可用节点上申请资源
                for node in $nodes; do
                    node_info=$(get_gpu_info "$node" "$gpu_arch")
                    available_gpus=$(echo $node_info | awk '{print $2}')

                    if [ "$available_gpus" -ge "$requested_gpus" ]; then
                        try_allocate "$node" "$partition" "gpu:$gpu_arch" "$requested_gpus" "$requested_mem"
                        if [ $? -eq 0 ]; then
                            allocation_success=true
                            exit 0
                        fi
                    fi
                done
            fi
        done
    else
        get_partition_gpu_info "$key"

        if [ "$auto_allocate" = true ]; then
            # 直接处理单个分区
            gpu_arch=$(get_gpu_arch "$key")
            nodes=$(sinfo -p "$key" -N -h -o "%N")

            for node in $nodes; do
                node_info=$(get_gpu_info "$node" "$gpu_arch")
                available_gpus=$(echo $node_info | awk '{print $2}')

                if [ "$available_gpus" -ge "$requested_gpus" ]; then
                    try_allocate "$node" "$key" "gpu:$gpu_arch" "$requested_gpus" "$requested_mem"
                    if [ $? -eq 0 ]; then
                        allocation_success=true
                        exit 0
                    fi
                fi
            done
        fi
    fi

    if [ "$auto_allocate" = true ] && [ "$allocation_success" = false ]; then
        echo -e "\033[1;31m所有节点资源申请失败！没有找到可用的资源。\033[0m"
        exit 1
    fi
}

# 修改参数处理逻辑
if [ -z "$1" ]; then
    echo "Error: Please provide a partition or group name as an argument. Use --help to see available options."
    exit 1
fi

# 处理帮助选项
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: $0 [OPTIONS] [PARTITION_GROUP_NAME] [GPU_NUMS] [MEMORY]"
    echo "Options:"
    echo "  --allocate [GPUS] [MEM_GB]  Automatically allocate resources"
    echo "  --help                      Show this help message"

    echo "Examples:"
    echo "  ./show_allocate_available_gpu.sh --help                         # check help"
    echo "  ./show_allocate_available_gpu.sh h100                           # check h100 GPU's availability"
    echo "  ./show_allocate_available_gpu.sh --allocate h100 1 30           # allocate GPU resource"
    echo "  ./show_allocate_available_gpu.sh -a h100 1 30                   # allocate GPU resource"
    echo "  ./show_allocate_available_gpu.sh -i h100 1 30                   # allocate GPU resource"

    echo  "Best Practise:"
    echo '  export GPU_TYPE=v100 GPU_NUM=1 MEM_GB=30 && echo $GPU_TYPE $GPU_NUM $MEM_GB'
    echo "  make check_gpu                                             # check gpu availability"
    echo "  make allocate_gpu                                          # allocate specific gpu resources"

    echo ""
    echo "Available PARTITION_GROUP_NAMES:"
    for key in "${!partition_dict[@]}"; do
        echo "  $key"
    done

    echo -e "\nAvailable partitions:"
    sinfo -h -o "%P" | grep -v "^PARTITION" | sort | uniq | sed 's/^/  /'
    exit 0
fi

echo "Debug: Processing argument: $@"

# 处理自动分配选项
if [ "$1" == "--allocate" ] || [ "$1" == "-a" ]; then
    shift
    partition_name=$1
    gpus=${2:-1}
    mem=${3:-30}
    process_partitions "$partition_name" true "$gpus" "$mem"
elif [[ "$1" = "-i" ]]; then
    # 支持直接传递数字参数的简写方式
    read -p "请输入GPU类型 [h100, a100, v100]: " gpu_type;
    partition_name=${gpu_type:-$2};
    read -p "请输入GPU数量 [1]: " gpu_num;
    gpus=${gpu_num:-$3};
    read -p "请输入内存大小(GB) [30]: " mem_gb;
    mem=${mem_gb:-$4};
    echo "partition_name=$$partition_name, gpus=$$gpus, mem=$mem"
    process_partitions "$partition_name" true "$gpus" "$mem"

else # check gpu availablitily
    process_partitions "$1"
fi