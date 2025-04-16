from pprint import pprint
import json
import sys
from collections import defaultdict
import re
sys.stdout.reconfigure(encoding='utf-8')

note_items = json.load(open('./res/output.json', 'r', encoding='utf-8'))

one_piece = json.load(
    open('./res/jsons/one_piece.json', 'r', encoding='utf-8'))

descriptions = open('./res/txts/descriptions.txt', 'w+', encoding='utf-8')


character_names = {
    "Gear 5 Luffy": ["gear 5", "hidden", "fifth"],
    "Monkey D. Luffy": ["luffy"],
    "Roronoa Zoro": ["zoro", "zorro", "roronoa"],
    "Jinbe": ["jinbe", "jinping"],
    "Sanji": ["sanji", "shanzhi"],
    "Tony Tony Chopper": ["chopper", "tony", "choba"],
    "Franky": ["franky", "franke", "frank"],
    "Nami": ["nami"],
    "Nico Robin": ["robin", "nico"],
    "Usopp": ["usopp", "lie", "cloth"],
    "Brooke": ["brook", "brooke"],
    "Trafalgar Law": ["trafalgar", "Trafalgaro"],
    "Sabo": ["sabo", "sabor", "sabau", "saab"],
}


def extract_data(text):
    data = {
        "weight": None,
        "desiccant_sound": False,
        "shake_up_down": None,
        "shake_left_right": None,
        "shake_front_back": None,
        "has_base_accessory": True,
        "fullness": None,
        "other_notes": [],
    }

    # Normalize text
    text = text.lower().replace('\n', ' ')

    # Weight
    weight_match = re.search(r'(\d{2,3}\.?\d?)\s*g', text)
    if weight_match:
        data["weight"] = float(weight_match.group(1))

    # Desiccant
    if "desiccant" in text or "particle sound" in text:
        data["desiccant_sound"] = True

    # Shake behaviors
    data["shake_up_down"] = "can't" if "can't shake up and down" in text else (
        "slightly" if "slightly" in text and "up and down" in text else "can")
    data["shake_left_right"] = "can't" if "can't feel" in text and "left and right" in text else "can"
    data["shake_front_back"] = "can't" if "not moving forward and back" in text else "can"

    # Base accessory
    if "only one without base accessory" in text or "no base" in text:
        data["has_base_accessory"] = False

    # Fullness
    if "very full" in text or "stuffed" in text:
        data["fullness"] = "very full"
    elif "slight shaking space" in text:
        data["fullness"] = "slight space"

    # Other Notes
    notes = re.findall(r"⚠️[^⚠️]+", text)
    data["other_notes"] = [note.strip() for note in notes]

    return data


def split_by_character(raw_text, character_names):
    character_data = defaultdict(list)

    # Sort names by length so we match 'gear 5 luffy' before just 'luffy'
    sorted_names = sorted(character_names, key=len, reverse=True)

    # Create regex pattern to match character mentions
    pattern = re.compile("|".join(map(re.escape, sorted_names)), re.IGNORECASE)

    current_character = None
    buffer = []

    for line in raw_text.split("\n"):
        match = pattern.search(line)
        if match:
            # Save the previous character block if we had one
            if current_character and buffer:
                character_data[current_character].append(
                    "\n".join(buffer).strip()
                )
                buffer = []

            current_character = match.group().lower()

        if current_character:
            buffer.append(line)

    # Save the last character's buffer
    if current_character and buffer:
        character_data[current_character].append("\n".join(buffer).strip())

    return character_data


if __name__ == '__main__':
    if False:
        for url in note_items:
            title = note_items[url]['title']['en']
            if re.search(r'One Piece', title, re.IGNORECASE):
                one_piece[url] = note_items[url]
            json.dump(one_piece, open(
                './res/jsons/one_piece.json', 'w', encoding='utf-8'))

    if False:
        for url in one_piece:
            desc = one_piece[url]['description']['en']
            descriptions.write("---" * 20 + '\n')
            descriptions.write(desc + '\n')

    if True:
        data = split_by_character(
            open("./res/txts/descriptions.txt", "r", encoding="utf-8").read(), character_names)
        json.dump(data, open("./res/jsons/descriptions.json",
                  "w+", encoding="utf-8"), indent=4)

        characters = {}
        for character, descriptions in data.items():
            desc = "".join(descriptions)
            data = extract_data(desc)
            characters[character] = data

        json.dump(characters, open(
            f"./res/jsons/characters/characters.json", "w+", encoding="utf-8"), indent=4)
