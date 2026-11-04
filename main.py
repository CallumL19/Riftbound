from pyparsing import infix_notation, OpAssoc, Keyword, Regex
import json
import re


# Load catalogue
with open("catalog.json", "r", encoding="utf-8") as file:
    data = json.load(file)

cards = data["cards"]
printings = data["printings"]


# Build a printing lookup for each card
printing_lookup = {}

for printing in printings.values():

    card_id = printing.get("cardId")

    if card_id not in printing_lookup:
        printing_lookup[card_id] = []

    printing_lookup[card_id].append(printing)


# Build a rules text lookup
rules_lookup = {}

for printing in printings.values():

    card_id = printing.get("cardId")

    if card_id not in rules_lookup:
        rules_lookup[card_id] = []

    text = printing.get("printedRulesText")
    effect = printing.get("printedEffectText")

    if text:
        rules_lookup[card_id].append(text)

    if effect:
        rules_lookup[card_id].append(effect)


def get_rules_text(card_id):

    return " ".join(rules_lookup.get(card_id, []))

def compare_number(value, filter_item, prefix):

    if value is None:
        return False

    if filter_item.startswith(prefix + "<="):
        return value <= int(filter_item[len(prefix) + 2:])

    elif filter_item.startswith(prefix + ">="):
        return value >= int(filter_item[len(prefix) + 2:])

    elif filter_item.startswith(prefix + "<"):
        return value < int(filter_item[len(prefix) + 1:])

    elif filter_item.startswith(prefix + ">"):
        return value > int(filter_item[len(prefix) + 1:])

    elif filter_item.startswith(prefix + ":"):
        return value == int(filter_item[len(prefix) + 1:])

    return False


def matches_filter(filter_item, card_id, card):

    exclude = filter_item.startswith("-")

    if exclude:
        filter_item = filter_item[1:]

    filter_matches = True

    # Domain
    if filter_item.startswith("d:"):
        domain = filter_item[2:]
        filter_matches = domain in [
            d.lower() for d in card["domains"]
        ]

    # Type
    elif filter_item.startswith("t:"):
        card_type = filter_item[2:]
        filter_matches = card_type in [
            t.lower() for t in card["types"]
        ]

    # Energy
    # Energy
    elif filter_item.startswith("e"):
        filter_matches = compare_number(
            card["energy"], filter_item, "e"
        )

    # Might
    elif filter_item.startswith("m"):
        filter_matches = compare_number(
            card["might"], filter_item, "m"
        )

    # Power
    elif filter_item.startswith("p"):
        filter_matches = compare_number(
            card["power"], filter_item, "p"
        )

    # Keyword
    elif filter_item.startswith("k:"):
        keyword = filter_item[2:]
        filter_matches = keyword in [
            k.lower() for k in card["keywords"]
        ]

    # Tag
    elif filter_item.startswith("tag:"):
        tag = filter_item[4:]
        filter_matches = tag in [
            t.lower() for t in card["tags"]
        ]

    # Set filter
    elif filter_item.startswith("s:"):

        set_code = filter_item[2:].upper()

        card_printings = printing_lookup.get(card_id, [])

        filter_matches = any(
            printing.get("shortCode", "").upper().startswith(set_code + "-")
            for printing in card_printings
        )

    # Rarity filter
    elif filter_item.startswith("r:"):

        rarity = filter_item[2:].lower()

        card_printings = printing_lookup.get(card_id, [])

        filter_matches = any(
            printing.get("rarity", "").lower() == rarity
            for printing in card_printings
        )

    # Rules text
    elif filter_item.startswith("o:"):
        search_text = filter_item[2:]
        rules_text = get_rules_text(card_id).lower()
        filter_matches = search_text in rules_text

    # Card name
    else:
        filter_matches = filter_item in card["name"].lower()

    if exclude:
        filter_matches = not filter_matches

    return filter_matches



def evaluate_query(expression, card_id, card):

    operator = expression[0]

    # Individual search condition
    if operator == "term":
        return matches_filter(expression[1], card_id, card)

    # AND condition
    elif operator == "and":
        return (
            evaluate_query(expression[1], card_id, card)
            and evaluate_query(expression[2], card_id, card)
        )

    # OR condition
    elif operator == "or":
        return (
            evaluate_query(expression[1], card_id, card)
            or evaluate_query(expression[2], card_id, card)
        )

# Convert a search query into tokens

def parse_query(query):

    # Split query into tokens
    tokens = re.findall(r'\(|\)|[^\s()]+', query.lower())

    position = 0

    def parse_primary():

        nonlocal position

        if position >= len(tokens):
            raise ValueError("Unexpected end of query")

        token = tokens[position]

        # Handle parentheses
        if token == "(":

            position += 1

            result = parse_or()

            if position >= len(tokens) or tokens[position] != ")":
                raise ValueError("Missing closing parenthesis")

            position += 1

            return result

        # Reject unexpected closing parentheses
        if token == ")":
            raise ValueError("Unexpected closing parenthesis")

        # Individual search term
        position += 1

        return ("term", token)

    def parse_and():

        nonlocal position

        result = parse_primary()

        # Spaces represent AND
        while position < len(tokens):

            token = tokens[position]

            if token == ")" or token == "or":
                break

            if token == "and":
                position += 1

            right = parse_primary()

            result = ("and", result, right)

        return result

    def parse_or():

        nonlocal position

        result = parse_and()

        while position < len(tokens) and tokens[position] == "or":

            position += 1

            right = parse_and()

            result = ("or", result, right)

        return result

    expression = parse_or()

    if position != len(tokens):
        raise ValueError("Invalid search query")

    return expression



def search_cards(query):

    results = []

    # Convert query into an expression tree
    expression = parse_query(query)

    # Check every card
    for card_id, card in cards.items():

        if evaluate_query(expression, card_id, card):
            results.append(card)

    return results




print("==============================")
print("       RIFTBOUND SEARCH")
print("==============================")

while True:

    query = input("\nEnter search query (or 'exit'): ")

    if query.lower() == "exit":
        break

    results = search_cards(query)

    print(f"\nFound {len(results)} matching cards:\n")

    for card in results[:20]:

        print("------------------------------")
        print("Name:", card["name"])
        print("Type:", card["types"])
        print("Domains:", card["domains"])
        print("Energy:", card["energy"])
        print("Keywords:", card["keywords"])
        print("------------------------------")
