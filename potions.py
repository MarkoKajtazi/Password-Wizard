import pygame, string

POWER_MAP = {
    "uppercase": 5,
    "special_characters": 10,
    "numbers": 15,
    "lowercase": 2
}

POTION_PRICES_MAP = {
    "uppercase": 50,
    "special_characters": 80,
    "numbers": 100,
}

def get_power(password):
    total_power = 0
    for char in password:
        if char.isupper(): total_power += POWER_MAP["uppercase"]
        elif char.isdigit(): total_power += POWER_MAP["numbers"]
        elif char in string.punctuation: total_power += POWER_MAP["special_characters"]
        elif char.islower(): total_power += POWER_MAP["lowercase"]
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