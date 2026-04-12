import requests
import json

url = "http://127.0.0.1:11434/api/chat"
payload = {
    "model": "gemma4:e4b",
    "messages": [{"role": "user", "content": "hi"}],
    "stream": False
}

print(f"Attempting to call {payload['model']}...")
try:
    response = requests.post(url, json=payload, timeout=30)
    if response.status_code == 200:
        print("Success! Model loaded and responded.")
        print(response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
