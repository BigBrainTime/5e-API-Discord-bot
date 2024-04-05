import requests

query = {
    "logic": {"userID":{">":0}}
}

response = requests.get(
    'http://127.0.0.1:5000/api/get_image_ids', json=query)

print(response.text)