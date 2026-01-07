import requests
import json

admin_email = "admin@allinone.com"
admin_password = "admin_allinone_2026"

login_url = "https://full-stack-project-iota-lime.vercel.app/api/users/login"
payload = {"email": admin_email, "password": admin_password}
headers = {"Content-Type": "application/json"}

try:
    print("Logging in as admin...")
    login_res = requests.post(login_url, json=payload, headers=headers)
    token = login_res.json()["access_token"]
    
    # Use the admin/users endpoint which often shows more info
    users_url = "https://full-stack-project-iota-lime.vercel.app/api/admin/users"
    get_headers = {"Authorization": f"Bearer {token}"}
    users_res = requests.get(users_url, headers=get_headers)
    
    if users_res.status_code == 200:
        users = users_res.json()
        print(f"Total users found: {len(users)}")
        for u in users:
            role = u.get("role")
            profile = u.get("provider_profile")
            if role == "provider":
                print(f"Provider User: {u['name']} (Email: {u['email']})")
                if profile:
                    print(f"  Profile Service: {profile['service_type']}, Verified: {profile['background_verified']}")
                else:
                    print(f"  CRITICAL: Provider user HAS NO PROFILE!")
            elif profile:
                print(f"User {u['name']} is {role} but HAS a provider profile! (Service: {profile['service_type']})")
    
    # Also check raw providers
    providers_url = "https://full-stack-project-iota-lime.vercel.app/api/providers/?service_type=security"
    prov_res = requests.get(providers_url)
    if prov_res.status_code == 200:
        provs = prov_res.json()
        print(f"\nProviders endpoint (security) returned {len(provs)} records:")
        for p in provs:
            user_name = p.get("user", {}).get("name") if p.get("user") else "NULL"
            print(f" - Provider ID: {p['id']}, User Name: {user_name}, Verified: {p['background_verified']}")

except Exception as e:
    print(f"Error: {e}")
