from config import CONFIG, update_config
from telethon import TelegramClient, events, utils
import asyncio
import re
from telethon.tl.types import MessageEntityTextUrl

client = TelegramClient('test', int(CONFIG["api"]), CONFIG["api_hash"])

async def get_urls():
    print()

async def private_incoming(event):
    cl = await update_config(client)
    return any(c.dfrom == event.chat_id for c in cl)

@client.on(events.NewMessage())
async def normal_handler(event):
    cl = await update_config(client)
    current_c = None
    for c in cl:
        if c.dfrom == event.chat_id:
            current_c = c
            break
        
    if any(c.dfrom == event.chat_id for c in cl):
        user_mess=event.message
        if current_c.only_url:
            urls = []
            for url_entity, _ in user_mess.get_entities_text(MessageEntityTextUrl):
                urls.append(url_entity.url)
            urls += re.findall("(?P<url>https?://[^\s]+)", user_mess.text)
            await client.send_message(entity=current_c.dto, message="\n".join(urls))
            return
        if event.photo:
                try:
                    image_base = event.message.media
                    await client.send_file(entity=current_c.dto, file=image_base.photo)
                except Exception:
                    ...

        await client.send_message(entity=current_c.dto, message=user_mess)

print("starting bot...")
client.start()
client.run_until_disconnected()
