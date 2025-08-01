# How to run

# Setup Env (server & client）
export HOST=10.16.118.42
export PORT=8010
export GUARDRAILS_CONFIG_ID=./

# Run server and client
cd ryan_bot/config/gpt_parallel
./start-server.sh
./start-client.sh
