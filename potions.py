import pygame, string

POWER_MAP = {
    "uppercase": 15,
    "special_characters": 25,
    "numbers": 35,
    "lowercase": 5
}

POTION_PRICES_MAP = {
    "uppercase": 25,
    "special_characters": 35,
    "numbers": 50,
    "limit": 5,
}

# Chain bonus multipliers based on number of different character types used
CHAIN_BONUS = {
    1: 1.0,    # Single type: no bonus
    2: 1.25,   # Two types: 25% bonus
    3: 1.5,    # Three types: 50% bonus
    4: 2.0     # All four types: 100% bonus
}

def count_char_types(password):
    """Count how many of each character type are in the password."""
    counts = {
        "lowercase": 0,
        "uppercase": 0,
        "special_characters": 0,
        "numbers": 0
    }
    for char in password:
        if char.islower():
            counts["lowercase"] += 1
        elif char.isupper():
            counts["uppercase"] += 1
        elif char.isdigit():
            counts["numbers"] += 1
        elif char in string.punctuation:
            counts["special_characters"] += 1
    return counts


def get_power(password):
    total_power = 0
    types_used = set()

    for char in password:
        if char.isupper():
            total_power += POWER_MAP["uppercase"]
            types_used.add("uppercase")
        elif char.isdigit():
            total_power += POWER_MAP["numbers"]
            types_used.add("numbers")
        elif char in string.punctuation:
            total_power += POWER_MAP["special_characters"]
            types_used.add("special_characters")
        elif char.islower():
            total_power += POWER_MAP["lowercase"]
            types_used.add("lowercase")

    # Apply chain bonus based on variety of character types
    num_types = len(types_used)
    if num_types > 0:
        multiplier = CHAIN_BONUS.get(num_types, 1.0)
        total_power = int(total_power * multiplier)

    return total_power

def buy_ingredient(ingredient_type, coins, inventory):
    price = POTION_PRICES_MAP.get(ingredient_type, 0)
    if coins >= price:
        coins -= price
        inventory[ingredient_type] += 1
    return coins, inventory


def sell_ingredient(ingredient_type, coins, inventory, current_text):
    if inventory[ingredient_type] > 0:
        refund = int(POTION_PRICES_MAP.get(ingredient_type, 0))
        coins += refund
        inventory[ingredient_type] -= 1

        new_text = ""
        removed = False

        char_list = list(current_text)
        for i in range(len(char_list) - 1, -1, -1):
            char = char_list[i]
            match = False

            if ingredient_type == "uppercase" and char.isupper():
                match = True
            elif ingredient_type == "numbers" and char.isdigit():
                match = True
            elif ingredient_type == "special_characters" and char in string.punctuation:
                match = True

            if match and not removed:
                char_list.pop(i)
                removed = True
                break

        current_text = "".join(char_list)

    return coins, inventory, current_text

def handle_typing(event, current_text, inventory):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_BACKSPACE:
            if current_text:
                # Return the deleted character's ingredient to inventory
                deleted_char = current_text[-1]
                if deleted_char.isupper():
                    inventory["uppercase"] += 1
                elif deleted_char.isdigit():
                    inventory["numbers"] += 1
                elif deleted_char in string.punctuation:
                    inventory["special_characters"] += 1
                # Lowercase doesn't need to be returned (it's free)
            return current_text[:-1]
        elif event.key == pygame.K_RETURN:
            return "SUBMITTED"

        char = event.unicode
        if char.isprintable() and char != "":
            can_type = False
            inv_key = None

            if char.isupper(): inv_key = "uppercase"
            elif char.isdigit(): inv_key = "numbers"
            elif char in string.punctuation: inv_key = "special_characters"
            elif char.islower(): can_type = True # Lowercase is free

            if inv_key:
                # Check if we have stock
                if inventory[inv_key] > 0:
                    inventory[inv_key] -= 1  # SUBTRACT HERE
                    can_type = True

            if can_type:
                return current_text + char
    return current_text