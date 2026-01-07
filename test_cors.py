import requests
import json

url = "https://full-stack-project-iota-lime.vercel.app/api/providers/?service_type=security"
headers = {
    "Origin": "https://all-in-one-household-services.netlify.app",
    "Access-Control-Request-Method": "GET",
    "Access-Control-Request-Headers": "Content-Type,Authorization"
}

print(f"Testing CORS preflight (OPTIONS) at {url}...")
try:
    response = requests.options(url, headers=headers)
    print(f"OPTIONS Status: {response.status_code}")
    print(f"OPTIONS Headers:\n{json.dumps(dict(response.headers), indent=2)}")
    
    print(f"\nTesting actual GET with Origin...")
    get_res = requests.get(url, headers={"Origin": "https://all-in-one-household-services.netlify.app"})
    print(f"GET Status: {get_res.status_code}")
    print(f"GET Headers:\n{json.dumps(dict(get_res.headers), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
