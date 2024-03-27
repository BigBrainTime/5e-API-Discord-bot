import requests

api_key = ""

headers = {
    "Authorization":api_key
}

query = {
    "imageID": "bf8de8da-3f53-4661-83d5-d0652726c020"
}

response = requests.get(
    'http://127.0.0.1:8080/api/image_data', headers=headers, json=query)

print(response.text)