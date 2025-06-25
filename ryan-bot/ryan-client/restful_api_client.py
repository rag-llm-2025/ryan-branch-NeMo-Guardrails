import requests

try:
    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json={
            "config_id": "config",  # add config_id parameter
            "messages": [{
                "role": "user",
                "content": "who are you?"
            }]
        }
    )
    response.raise_for_status()  # check HTTP error

    # handle different response format
    response_data = response.json()
    print("response_data: ", response_data)

    if "messages" in response_data:
        print("Final Answser: ", response_data["messages"][0]["content"])
    elif "choices" in response_data:
        print("Final Answser: ", response_data["choices"][0]["message"]["content"])
    else:
        print("Unknow format: ", response_data)

except requests.exceptions.RequestException as e:
    print(f"Request Error: {str(e)}")
except Exception as e:
    print(f"Process response error: {str(e)}")
