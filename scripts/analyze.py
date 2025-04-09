import pandas as pd
import json
from pprint import pprint
# Combine lines by character
from collections import defaultdict
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Adjusting code to handle 'None' values for description fields
records = {}
data = json.load(open("./res/output.json", "r"))
# Parse each entry to extract relevant info
description = ''
zh_description = ''

"""
pattern = r"(Luffy|Zoro|Zorro|Nami|Robin|Brook|Chopper|Sanji|Jinbei|Franky|Sabo|Trafalgar|Gear|Tony|Nico|Jinpei|Franke|Lie|Shanzhi|Roronoa|Monkey|Five|Usopp|Cloth)"
for url, content in data.items():
    description_en = content["description"]["en"]
    zh_description += content["description"]["zh"]
    if description_en:
        description += description_en
    else:
        description_en = ""
    match = re.search(
        pattern, description_en, re.IGNORECASE)
    if match:
        records[url] = content


# pprint(records)
with open("./res/descriptions.txt", "w+", encoding="utf-8") as f:
    f.write(description)
with open("./res/descriptions_zh.txt", "w+", encoding="utf-8") as f:
    f.write(zh_description)
json.dump(records, open("./res/records.json", "w+"), indent=4)"""

gear = ''
pattern = r"(Luffy|Gear|Five)"
for url, content in data.items():
    if content["description"]["en"]:
        if re.search(pattern, content["description"]["en"], re.IGNORECASE):
            gear += "\n\n" + "===" * 50 + "\n\n"
            gear += content["description"]["en"]

with open("./res/gear.txt", "w+", encoding="utf-8") as f:
    print("gear")
    f.write(gear)

"""        
char_descriptions = defaultdict(list)

for record in records:
    line = record["description"]
    match = re.search(r"(Luffy|Zorro|Nami|Robin|Brook|Chopper|Sanji|Jinbei|Franky|Sabo|Trafalgar|Lie|Tony|Nico)(?:.*?)(?=[:\-|,])?", line, re.IGNORECASE)
    if match:
        char = match.group(0).strip().title()
        char_descriptions[char].append(line)

# Create a CSV from the combined data
csv_data = [{"Character": char, "How to Identify": " ".join(descs)} for char, descs in char_descriptions.items()]
df = pd.DataFrame(csv_data)
csv_path = "res/one_piece_labubu_guide_1.csv"
df.to_csv(csv_path, index=False)"""
