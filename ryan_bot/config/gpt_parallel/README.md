# How to run

# Run server and client
cd ryan_bot/config/gpt_parallel
uvicorn server:app --host 10.16.118.41 --port 8080
python client.py