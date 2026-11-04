
import json

# Load our downloaded catalogue
with open("catalog.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Display all the sections
print("CATALOGUE SECTIONS")
print("------------------")

for key, value in data.items():
    if isinstance(value, list):
        print(f"{key}: {len(value)} entries")
    else:
        print(f"{key}: {type(value).__name__}")
