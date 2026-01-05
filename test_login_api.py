import requests

def test_login():
    url = "http://127.0.0.1:8000/users/login"
    data = {
        "email": "admin@allinone.com",
        "password": "adminpassword"
    }
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

if __name__ == "__main__":
    test_login()
