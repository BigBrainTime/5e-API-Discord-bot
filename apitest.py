import requests

query = {
    "logic": {"userID":{">":0}}
}

response = requests.get(
    'http://127.0.0.1:8080/api/database/suggestions', json=query)

print(response.text)