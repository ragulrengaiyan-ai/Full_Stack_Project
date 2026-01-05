import requests
import json
import random

BASE_URL = "http://localhost:8000"

def test_flow():
    # 1. Register a Provider with Address
    provider_email = f"provider_{random.randint(100, 999)}@example.com"
    provider_data = {
        "name": "Test Provider",
        "email": provider_email,
        "password": "password123",
        "phone": "9876543210",
        "service_type": "housekeeper",
        "experience_years": 5,
        "hourly_rate": 500,
        "location": "Chennai",
        "address": "123, Anna Salai, Chennai, Tamil Nadu",
        "bio": "Expert housekeeper with 5 years experience."
    }
    
    print(f"Testing Provider Registration: {provider_email}")
    res = requests.post(f"{BASE_URL}/users/register/provider", json=provider_data)
    if res.status_code != 201:
        print(f"FAILED: {res.text}")
        return
    provider_id = res.json()["id"]
    print(f"SUCCESS: Provider registered with ID {provider_id}")

    # 2. Register a Customer
    customer_email = f"customer_{random.randint(100, 999)}@example.com"
    customer_data = {
        "name": "Test Customer",
        "email": customer_email,
        "password": "password123",
        "phone": "9000000000"
    }
    print(f"\nTesting Customer Registration: {customer_email}")
    res = requests.post(f"{BASE_URL}/users/register/customer", json=customer_data)
    customer_id = res.json()["id"]
    print(f"SUCCESS: Customer registered with ID {customer_id}")

    # 3. Create a Booking
    booking_data = {
        "provider_id": provider_id,
        "service_name": "housekeeper",
        "booking_date": "2026-01-10",
        "booking_time": "10:00:00",
        "duration_hours": 2,
        "address": "456, OMR, Chennai",
        "notes": "Testing a booking"
    }
    print("\nTesting Booking Creation")
    res = requests.post(f"{BASE_URL}/bookings/?customer_id={customer_id}", json=booking_data)
    booking_id = res.json()["id"]
    print(f"SUCCESS: Booking created with ID {booking_id}")

    # 4. Mark Booking as Completed (Provider flow)
    print("\nUpdating Booking status to 'completed'")
    res = requests.patch(f"{BASE_URL}/bookings/{booking_id}/status?new_status=completed")
    print(f"SUCCESS: {res.json()['message']}")

    # 5. Submit a Review
    review_data = {
        "booking_id": booking_id,
        "rating": 5,
        "comment": "Excellent service! Very professional."
    }
    print("\nTesting Review Submission")
    res = requests.post(f"{BASE_URL}/reviews/?customer_id={customer_id}", json=review_data)
    if res.status_code == 201:
        print("SUCCESS: Review submitted successfully")
    else:
        print(f"FAILED: {res.text}")

    # 6. Check Provider Rating
    print("\nVerifying Provider Rating")
    res = requests.get(f"{BASE_URL}/providers/{provider_id}")
    new_rating = res.json()["provider"]["rating"]
    print(f"Provider Rating is now: {new_rating}")

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"Error connecting to server: {e}")
        print("Make sure the FastAPI server is running at http://localhost:8000")
