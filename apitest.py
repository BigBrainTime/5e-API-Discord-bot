import requests

query = {
    "logic": {"creature":"owlbear"}
}

response = requests.get(
    'http://127.0.0.1:8080/api/image_data', json=query)

print(response.text)