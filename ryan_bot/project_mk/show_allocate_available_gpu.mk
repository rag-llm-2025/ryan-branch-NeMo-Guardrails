# Description:
# cmd: make check_gpu GPU_TYPE=v100
# cmd: make allocate_gpu GPU_TYPE=v100 GPU_NUM=1 MEM_GB=30

# 添加参数默认值
GPU_TYPE ?= h100
GPU_NUM ?= 1
MEM_GB ?= 30

# 添加检查GPU可用性的目标
.PHONY: check_gpu
check_gpu:
	@echo "检查 GPU_TYPE=$(GPU_TYPE) GPU可用性..."

	@./show_allocate_available_gpu.sh $(GPU_TYPE)

.PHONY: allocate_gpu
allocate_gpu:
	@echo "正在自动申请GPU资源..."
	@echo "GPU_TYPE=$(GPU_TYPE), GPU_NUM=$(GPU_NUM), MEM_GB=$(MEM_GB)"
	@./show_allocate_available_gpu.sh --allocate $(GPU_TYPE) $(GPU_NUM) $(MEM_GB)