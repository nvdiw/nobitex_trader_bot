import requests
import json

API_KEY = "Your API"

url = "https://apiv2.nobitex.ir/users/wallets/list"

headers = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

response = requests.post(url, headers=headers, json={})

if response.status_code == 200:
    data = response.json()

    # Save JSON to file
    with open("wallets_data.json", "w") as file:
        json.dump(data, file, indent=4)

    print("Data saved to wallets_data.json")
else:
    print("Error:", response.text)
