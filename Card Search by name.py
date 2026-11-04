
import json

# Load the catalogue
with open("catalog.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Get all cards
cards = data["cards"]

print("==============================")
print("       RIFTBOUND SEARCH")
print("==============================")

while True:

    search = input("\nEnter a card name (or 'exit' to quit): ")

    if search.lower() == "exit":
        print("Goodbye!")
        break

    # Find matching cards
    results = []

    for card_id, card in cards.items():

        if search.lower() in card["name"].lower():
            results.append(card)

    # Display results
    if results:

        print(f"\nFound {len(results)} matching cards:\n")

        for card in results:

            print("------------------------------")
            print("Name:", card["name"])
            print("Type:", card["types"])
            print("Domains:", card["domains"])
            print("Energy:", card["energy"])
            print("Might:", card["might"])
            print("Power:", card["power"])
            print("Keywords:", card["keywords"])
            print("------------------------------")

    else:
        print("\nNo matching cards found.")
