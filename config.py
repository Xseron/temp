import json
import yaml
import platform
import os
import asyncio
from concurrent.futures import ProcessPoolExecutor
from telethon import utils

last_modyfied = None
is_chatids_changed = False
chatss = []

with open("data/config.json", "r") as cfg:
    CONFIG = json.load(cfg)

def modification_date(path_to_file):
    if platform.system() == 'Windows':
        return os.path.getmtime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        return stat.st_mtime

class Chat():
    def __init__(self, cfrom, cto, only_url):
        self.cfrom = cfrom
        self.cto = cto
        self.only_url = only_url
        
        self.dfrom = None
        self.dto = None
    def __str__(self) -> str:
        return str({"cfrom": self.cfrom, "cto": self.cto, "only_url": self.only_url, "dfrom": self.dfrom, "dto": self.dto})
    def is_full(self):
        return (self.cfrom is not None and
                self.cto is not None and
                self.only_url is not None and
                self.dfrom is not None and
                self.dto is not None)
async def update_config(client):
    if not client.is_connected():
        await client.connect()

    global chatss
    global last_modyfied
    temp = []

    if last_modyfied != modification_date("data/chats.yaml"):
        last_modyfied = modification_date("data/chats.yaml")
        with open('data/chats.yaml', mode='r', encoding="UTF-8") as chatss:
            chats_from_file = yaml.load(chatss.read(), Loader=yaml.Loader)["chats"]
        
        chats_ls = [Chat(chat["from"], chat["to"], chat["only_url"])  for chat in chats_from_file]
        
        async for dialog in client.iter_dialogs():
            for index, (cfrom, cto) in enumerate(zip([ch.cfrom for ch in chats_ls], [ch.cto for ch in chats_ls])):
                if cfrom in dialog.name:
                    chats_ls[index].dfrom = utils.get_peer_id(dialog.entity)
                if cto in dialog.name:
                    chats_ls[index].dto = utils.get_peer_id(dialog.entity)
        
        for chat in chats_ls:
            if not chat.is_full():
                print(f"{chat} is not full or there a mistake")
            else: 
                temp.append(chat)
                
        print("Config changed!")
        chatss = temp.copy()
        return temp
    print("Config stayes!")
    return chatss

if __name__ == "__main__":
    from telethon import TelegramClient, events
    from telethon.sessions import StringSession

    client = TelegramClient('session_name', 10088381, "d217fb9cc10167c19e03a8c194078060")

    async def main():
        await client.start()
        print("Client connected successfully.")
        asyncio.create_task(update_config(client))
        await client.run_until_disconnected()

    asyncio.run(main())