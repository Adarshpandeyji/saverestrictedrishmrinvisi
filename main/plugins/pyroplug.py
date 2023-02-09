

import asyncio, time, os

from pyrogram.enums import ParseMode , MessageMediaType

from .. import Bot, bot
from main.plugins.progress import progress_for_pyrogram
from main.plugins.helpers import screenshot

from pyrogram import Client, filters
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, FloodWait
#from ethon.pyfunc import video_metadata
from main.plugins.helpers import video_metadata
from telethon import events

import logging

logging.basicConfig(level=logging.debug,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.INFO)
logging.getLogger("telethon").setLevel(logging.INFO)

def thumbnail(sender):
    return f'{sender}.jpg' if os.path.exists(f'{sender}.jpg') else None
      
async def check(userbot, client, link):
    logging.info(link)
    msg_id = 0
    try:
        msg_id = int(link.split("/")[-1])
    except ValueError:
        if '?single' not in link:
            return False, "**Invalid Link!**"
        link_ = link.split("?single")[0]
        msg_id = int(link_.split("/")[-1])
    if 't.me/c/' in link:
        try:
            chat = int('-100' + str(link.split("/")[-2]))
            await userbot.get_messages(chat, msg_id)
            return True, None
        except ValueError:
            return False, "**Invalid Link!**"
        except Exception as e:
            logging.info(e)
            return False, "Have you joined the channel?"
    else:
        try:
            chat = str(link.split("/")[-2])
            await client.get_messages(chat, msg_id)
            return True, None
        except Exception as e:
            logging.info(e)
            return False, "Maybe bot is banned from the chat, or your link is invalid!"
            
async def get_msg(userbot, client, sender, edit_id, msg_link, i, file_n):
    edit = ""
    chat = ""
    msg_id = int(i)
    if msg_id == -1:
        await client.edit_message_text(sender, edit_id, "**Invalid Link!**")
        return None
    if 't.me/c/'  in msg_link or 't.me/b/' in msg_link:
        

        if "t.me/b" not in msg_link:    
            chat = int('-100' + str(msg_link.split("/")[-2]))
        else:
            chat = int(msg_link.split("/")[-2])
        file = ""
        try:
            msg = await userbot.get_messages(chat_id = chat, message_ids = msg_id)
            logging.info(msg)
           # medi =  msg.document or msg.video or msg.audio or None
            if msg.service is not None:
                await client.delete_messages(
                    chat_id=sender,
                    message_ids=edit_id
                )
                #await client.edit_message_text(sender, edit_id, f"{msg.service}")
                return None
            if msg.empty is not None:
                await client.delete_messages(
                    chat_id=sender,
                    message_ids=edit_id
                )
                #await client.edit_message_text(sender, edit_id, f"message dosnt exist \n{msg.empty}")
                return None            
            
            if msg.media and msg.media==MessageMediaType.WEB_PAGE:
                a = b = True
                edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                if '--'  in msg.text.html or '**' in msg.text.html or '__' in msg.text.html or '~~' in msg.text.html or '||' in msg.text.html or '```' in msg.text.html or '`' in msg.text.html:
                    await client.send_message(sender, msg.text.html, parse_mode=ParseMode.HTML)
                    a = False
                if '<b>' in msg.text.markdown or '<i>' in msg.text.markdown or '<em>' in msg.text.markdown  or '<u>' in msg.text.markdown or '<s>' in msg.text.markdown or '<spoiler>' in msg.text.markdown or '<a href=>' in msg.text.markdown or '<pre' in msg.text.markdown or '<code>' in msg.text.markdown or '<emoji' in msg.text.markdown:
                    await client.send_message(sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                    b = False
                if a and b:
                    await client.send_message(sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                await edit.delete()
                return None
            if not msg.media and msg.text:
                a = b = True
                edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                if '--'  in msg.text.html or '**' in msg.text.html or '__' in msg.text.html or '~~' in msg.text.html or '||' in msg.text.html or '```' in msg.text.html or '`' in msg.text.html:
                    await client.send_message(sender, msg.text.html, parse_mode=ParseMode.HTML)
                    a = False
                if '<b>' in msg.text.markdown or '<i>' in msg.text.markdown or '<em>' in msg.text.markdown  or '<u>' in msg.text.markdown or '<s>' in msg.text.markdown or '<spoiler>' in msg.text.markdown or '<a href=>' in msg.text.markdown or '<pre' in msg.text.markdown or '<code>' in msg.text.markdown or '<emoji' in msg.text.markdown:
                    await client.send_message(sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                    b = False
                if a and b:
                    await client.send_message(sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                
                '''await client.send_message(sender, msg.text.html, parse_mode = 'html')
                   await client.send_message(sender, msg.text.html, parse_mode = 'md')
                   await client.send_message(sender, msg.text.markdown, parse_mode = 'html')
                   await client.send_message(sender, msg.text.markdown, parse_mode = 'md')
                   await client.send_message(sender, msg.text.markdown)
                '''
                await edit.delete()
                return None
            if msg.media==MessageMediaType.POLL:
                #await client.send_message(sender,'poll media cant be saved')
                await client.edit_message_text(sender, edit_id, 'poll media cant be saved')
                #await edit.delete()
                return 
            edit = await client.edit_message_text(sender, edit_id, "Trying to Download.")
            
            file = await userbot.download_media(
                msg,
                progress=progress_for_pyrogram,
                progress_args=(
                    client,
                    "**DOWNLOADING:**\n",
                    edit,
                    time.time()
                )
            )
            path = file
            #await edit.edit('Preparing to Upload!')
            await edit.delete()
            upm = await client.send_message(sender, 'Preparing to Upload!')
            
            caption = str(file)
            if msg.caption is not None:
                caption = msg.caption
            if str(file).split(".")[-1] in ['mkv', 'mp4', 'webm', 'mpe4', 'mpeg']:
                if str(file).split(".")[-1] in ['webm', 'mkv', 'mpe4', 'mpeg']:
                    path = str(file).split(".")[0] + ".mp4"
                    os.rename(file, path) 
                    file = str(file).split(".")[0] + ".mp4"
                data = video_metadata(file)
                duration = data["duration"]
                wi= data["width"]
                hi= data["height"]
                logging.info(data)

                if file_n != '':
                    #path = ''
                    if '.' in file_n:
                        
                        path = f'/app/downloads/{file_n}'
                    else:
                        
                        path = f'/app/downloads/{file_n}.' + str(file).split(".")[-1]

                    os.rename(file, path)
                    file = path
                try:
                    thumb_path = await screenshot(file, duration, sender)
                except Exception as e:
                    logging.info(e)
                    thumb_path = None
                caption = msg.caption if msg.caption is not None else str(file).split("/")[-1]
                await client.send_video(
                    chat_id=sender,
                    video=path,
                    caption=caption,
                    supports_streaming=True,
                    duration=duration,
                    height=hi,
                    width=wi,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**UPLOADING:**\n',
                        upm,
                        time.time()
                    )
                )
            elif str(file).split(".")[-1] in ['jpg', 'jpeg', 'png', 'webp']:
                if file_n != '':
                    #path = ''
                    if '.' in file_n:
                        path = f'/app/downloads/{file_n}'
                    else:
                        path = f'/app/downloads/{file_n}.' + str(file).split(".")[-1]

                    os.rename(file, path)
                    file = path

                
                

                caption = msg.caption if msg.caption is not None else str(file).split("/")[-1]
                await upm.edit("Uploading photo.")

                await bot.send_file(sender, path, caption=caption)
            else:
                if file_n != '':
                    #path = ''
                    if '.' in file_n:
                        path = f'/app/downloads/{file_n}'
                    else:
                        path = f'/app/downloads/{file_n}.' + str(file).split(".")[-1]

                    os.rename(file, path)
                    file = path
                thumb_path=thumbnail(sender)
                caption = msg.caption if msg.caption is not None else str(file).split("/")[-1]
                await client.send_document(
                    sender,
                    path, 
                    caption=caption,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**UPLOADING:**\n',
                        upm,
                        time.time()
                    )
                )
            os.remove(file)
            await upm.delete()
            return None
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await client.edit_message_text(sender, edit_id, "Bot is not in that channel/ group \n send the invite link so that bot can join the channel ")
            return None
    else:
        edit = await client.edit_message_text(sender, edit_id, "Cloning.")
        chat =  msg_link.split("/")[-2]
        await client.copy_message(int(sender), chat, msg_id)
        await edit.delete()
        return None   
 
async def get_bulk_msg(userbot, client, sender, msg_link, i):
    x = await client.send_message(sender, "Processing!")
    file_name = ''
    await get_msg(userbot, client, sender, x.id, msg_link, i, file_name) 
