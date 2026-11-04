
import requests
import json

# OpenRift API
url = "https://openrift.app/api/v1/catalog"

headers = {
    "User-Agent": "RiftboundSearch/1.0"
}

print("Downloading Riftbound card catalogue...")

response = requests.get(url, headers=headers, timeout=30)

if response.status_code == 200:

    data = response.json()

    print("\nSuccessfully downloaded catalogue!")

    # Save the complete catalogue locally
    with open("catalog.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("Saved catalogue.json")

    # Display some information
    print("\nTop-level data structure:")

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                print(f"{key}: {len(value)} entries")
            else:
                print(f"{key}: {type(value).__name__}")

    print("\nDownload complete!")

else:
    print("Error:", response.status_code)
    print(response.text)
