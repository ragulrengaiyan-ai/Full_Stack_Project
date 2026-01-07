import requests
import json

url = "https://full-stack-project-iota-lime.vercel.app/api/providers/?service_type=security"
print(f"Fetching raw JSON from: {url}")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Raw JSON data:\n{json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")
