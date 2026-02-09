import requests

# URL of the API
BASE_URL = "http://127.0.0.1:8000/api"

# Admin credentials
ADMIN_EMAIL = "admin@allinone.com"
ADMIN_PASSWORD = "admin123"

def get_token():
    url = f"{BASE_URL}/users/token"
    data = {
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Login failed: {response.text}")
        return None

def get_complaints(token):
    url = f"{BASE_URL}/complaints"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        print("Logged in successfully.")
        get_complaints(token)
