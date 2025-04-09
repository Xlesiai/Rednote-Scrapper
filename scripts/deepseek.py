from ollama import ChatResponse, chat
import json
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    description = ""
    with open("./res/descriptions.txt", "r", encoding="utf-8") as f:
        description = f.read()
    response: ChatResponse = chat(
        model='deepseek-r1:14b',
        messages=[
            {
                'role': 'user',
                'content':
                f"""i webscraped 200 items from xiaohongshu explaining how to find each character from the one piece labubu set (https://www.popmart.com/us/pop-now/set/176)
                can you make a csv with each labubu one piece figurine and have a description on how to find them? columns ['character', 'weight+-', 'how to find'] 
                the charaters are [Luffy, Zorro, Nami, Robin, Brook, Chopper, Sanji, Jinbei, Franky, Sabo, Trafalgar, Gear 5 Luffy] 
                \n Content: {description}"""
            }]
    )
    print(response.message.content)
