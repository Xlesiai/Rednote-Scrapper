from pprint import pprint
import json
import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

note_items = json.load(open('./res/output.json', 'r', encoding='utf-8'))

one_piece = json.load(
    open('./res/jsons/one_piece.json', 'r', encoding='utf-8'))

weights = open('./res/txts/weights.txt', 'w+', encoding='utf-8')

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
            desc = one_piece[url]['description']['en']
            weights.write("---"*20 + '\n')
            weights.write(desc + '\n')
