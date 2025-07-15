# server_client.mk - 服务端和客户端运行命令

.PHONY: server
server: print_env update_yaml_config
	@echo "=== 环境变量调试 ==="
	@echo "HOST: $(HOST)"
	@echo "PORT: $(PORT)"
	@echo "LLM_DIR: $(LLM_DIR)"
	@echo "当前目录: $(shell pwd)"
	mkdir -p $(LOG_DIR)
	rm -f $(LOG_DIR)/ryan_server_*.log
	cd $(LLM_DIR)/src/nemo-guardrails && \
	nemoguardrails server --config=./ryan_bot/config --disable-chat-ui --default-config-id=qwen_model --host $(HOST) --port $(PORT) --verbose 2>&1 | tee $(LOG_DIR)/ryan_server_$(DATESTR).log

.PHONY: client
client: print_env update_yaml_config
	mkdir -p $(LOG_DIR)
	rm -f $(LOG_DIR)/ryan_client_*.log
	cd $(LLM_DIR)/src/nemo-guardrails && \
	python3 ./ryan_bot/ryan-client/ryan_demo_client.py --server-url http://${HOST}:${PORT} --api-key ${API_KEY} --api-secret ${API_SECRET} 2>&1 | tee $(LOG_DIR)/ryan_client_$(DATESTR).log