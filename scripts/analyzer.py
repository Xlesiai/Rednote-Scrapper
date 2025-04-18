from collections import defaultdict
from pprint import pprint
import numpy as np
import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

note_items = json.load(open('./res/output.json', 'r', encoding='utf-8'))

one_piece = json.load(
    open('./res/jsons/one_piece.json', 'r', encoding='utf-8'))

descriptions = open('./res/txts/descriptions.txt', 'w', encoding='utf-8')


character_names = {
    "Gear 5 Luffy": {"names": ["gear 5", "hidden", "fifth"],
                     "pattern": {"start": None, "stop": None}},
    "Monkey D. Luffy": {"names": ["luffy"],
                        "pattern": {"start": None, "stop": None}},
    "Roronoa Zoro": {"names": ["zoro", "zorro", "roronoa"],
                     "pattern": {"start": None, "stop": None}},
    "Jinbe": {"names": ["jinbe", "jinping", "jinpei"],
              "pattern": {"start": None, "stop": None}},
    "Sanji": {"names": ["sanji", "shanzhi", "yanzhi"],
              "pattern": {"start": None, "stop": None}},
    "Tony Tony Chopper": {"names": ["chopper", "tony", "choba"],
                          "pattern": {"start": None, "stop": None}},
    "Franky": {"names": ["franky", "franke", "frank"],
               "pattern": {"start": None, "stop": None}},
    "Nami": {"names": ["nami"],
             "pattern": {"start": None, "stop": None}},
    "Nico Robin": {"names": ["robin", "nico"],
                   "pattern": {"start": None, "stop": None}},
    "Usopp": {"names": ["usopp", "lie cloth"],
              "pattern": {"start": None, "stop": None}},
    "Brooke": {"names": ["brook", "brooke"],
               "pattern": {"start": None, "stop": None}},
    "Trafalgar Law": {"names": ["trafalgar", "Trafalgaro"],
                      "pattern": {"start": None, "stop": None}},
    "Sabo": {"names": ["sabo", "sabor", "sabau", "saab"],
             "pattern": {"start": None, "stop": None}},
}
# character_names = [k for k in character_names.keys()]


def filter_description(text):
    # Filter out emojis
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F700-\U0001F77F"  # alchemical symbols
        u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA00-\U0001FA6F"  # Chess Symbols
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub(r' ', text)

    # Filter out hashtags ("#(.+)(?:\n)")
    hashtag_pattern = re.compile(r"#\w+")

    text = hashtag_pattern.sub(r' ', text)
    # Filter phrases
    phrases = [
        "One Piece", "Labubu", "Blind Box", "Trendy toys", "Popular Mart",
    ]
    # Standardize text (lowercase)
    return text


def extract_weight(weights):
    # Remove values out of range
    weights = [x for x in weights if x > 70 and x < 140]

    # Calculate Q1 (25th percentile) and Q3 (75th percentile)
    Q1 = np.percentile(weights, 25)
    Q3 = np.percentile(weights, 75)
    IQR = Q3 - Q1

    # Define bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter out outliers
    filtered_data = [x for x in weights if lower_bound <= x <= upper_bound]
    return np.mean(filtered_data).round(2)


def extract_data(text):
    data = {
        "weight": None,
        "desiccant sound": False,
        "shake up down": None,
        "shake left right": None,
        "shake front back": None,
        "fullness": None,
        "notes": {},
    }

    # Normalize text
    text = text.lower().replace('\n', ' ')

    # Weight
    weight_match = re.findall(r'(\d{2,3}\.?\d?)', text)
    if len(weight_match) > 0:
        data["weight"] = extract_weight(
            [float(w) for w in weight_match])

    # Desiccant
    if "desiccant" in text or "particle sound" in text:
        data["desiccant sound"] = True

    # Shake behaviors
    data["shake up down"] = "can't" if "can't shake up and down" in text else (
        "slightly" if "slightly" in text and "up and down" in text else "can")
    data["shake left right"] = "can't" if "can't feel" in text and "left and right" in text else "can"
    data["shake front back"] = "can't" if "not moving forward and back" in text else "can"

    # Fullness
    if "very full" in text or "stuffed" in text:
        data["fullness"] = "very full"
    elif "slight shaking space" in text:
        data["fullness"] = "slight space"

    # Other Notes
    notes = re.findall(r"(\w+):(.*?)(?=\s\w+:|$)", text)
    for note in notes:
        if note[0] not in data["notes"]:
            data["notes"][note[0]] = note[1].strip()
        else:
            data["notes"][note[0]] += ", " + note[1].strip()

    return data


def split_by_character(raw_text: str, character_names: dict):
    character_data = defaultdict(list)
    current_character = None
    buffer = []

    # Create patterns for each character name
    for value in character_names.values():
        # Create regex pattern to match character mentions
        value['pattern']['start'] = re.compile(
            '|'.join(map(re.escape, value['names'])), re.IGNORECASE)

        others = []
        for v in character_names.values():
            if v['names'] != value['names']:
                others.extend(v['names'])

        value['pattern']['stop'] = re.compile(
            '|'.join(map(re.escape, others)), re.IGNORECASE)

    # Iterate over each line
    for line in raw_text.split('\n'):
        # Check if the line contains any of the character names
        for name, value in character_names.items():
            start_pattern: re.Pattern = value['pattern']['start']
            stop_pattern: re.Pattern = value['pattern']["stop"]

            start = start_pattern.search(line)
            if start:
                stop = stop_pattern.search(line)
                if stop:
                    line = line[:stop.start()]

                # Save the previous character block if we had one
                if current_character and buffer:
                    character_data[current_character].append(
                        "\n".join(buffer).strip()
                    )
                    buffer = []

                current_character = name

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

    if True:
        for url in one_piece:
            desc = filter_description(one_piece[url]['description']['en'])
            # descriptions.write("---" * 20 + '\n')
            descriptions.write(desc.replace('. ', '.\n') + '\n')

    if True:
        data = split_by_character(
            open("./res/txts/descriptions.txt", "r", encoding="utf-8").read(), character_names)
        json.dump(data, open("./res/jsons/descriptions.json",
                  "w+", encoding="utf-8"), indent=4)

        characters = {}
        for character, descriptions in data.items():
            desc = " ".join(descriptions)
            data = extract_data(desc)
            characters[character] = data

        json.dump(characters, open(
            f"./res/jsons/characters/characters.json", "w+", encoding="utf-8"), indent=4)

    if True:
        characters = json.load(open(
            f"./res/jsons/characters/characters.json", "r", encoding="utf-8"))

        for character, data in characters.items():
            print('##', character)

            for key, value in data.items():
                if key == 'notes':
                    print('### Notes')
                    for note, value in value.items():
                        print(f'\t> {note}:', value)
                    continue
                else:
                    print(f'\t### {key}: {value}')
            print()
