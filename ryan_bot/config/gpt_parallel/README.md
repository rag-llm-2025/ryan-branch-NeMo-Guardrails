# How to run

# Run server and client
cd ryan_bot/config/gpt_parallel
uvicorn server:app --host 0.0.0.0 --port 8000
python client.py