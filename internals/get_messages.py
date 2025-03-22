import json
from PIL import Image
import asyncio

# from .pixel_image import pixel_image

def getmessages():
    msgs = open("messages.json")
    accs = open("accounts.json")
    messages = json.load(msgs)
    accounts = json.load(accs)
    i = 0
    for item in messages:
        i += 1
        for account in accounts:
            if item["userid"] == account["id"]:
                item["userid"] = account["name"]
        if "https://" in item["message"]:
            for word in item["message"].split(" "):
                if word.startswith("https://"):
                    
                    item["message"] = item["message"]
        for word in item["message"].split(" "):
            if word.startswith(":") and word.endswith(":"):
                filename = word.replace(":","")
                try:
                    #item["message"] = item["message"].replace(word, pixel_image(Image.open(fr"./emojis/meow-{filename}.png"), False, ()))
                    pass
                except FileNotFoundError:
                    pass
                
    return messages