import os
from os import path
from pyrogram import Client, filters
from pyrogram.types import Message, Voice, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant
from callsmusic import callsmusic, queues
from callsmusic.callsmusic import client as USER
from helpers.admins import get_administrators
import requests
import aiohttp
import yt_dlp
from youtube_search import YoutubeSearch
import converter
from downloaders import youtube
from config import DURATION_LIMIT
from helpers.filters import command
from helpers.decorators import errors
from helpers.errors import DurationLimitError
from helpers.gets import get_url, get_file_name
import aiofiles
import ffmpeg
from PIL import Image, ImageFont, ImageDraw


def transcode(filename):
    ffmpeg.input(filename).output("input.raw", format='s16le', acodec='pcm_s16le', ac=2, ar='48k').overwrite_output().run() 
    os.remove(filename)

# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text((190, 550), f"Title: {title}", (255, 255, 255), font=font)
    draw.text(
        (190, 590), f"Duration: {duration}", (255, 255, 255), font=font
    )
    draw.text((190, 630), f"Views: {views}", (255, 255, 255), font=font)
    draw.text((190, 670),
        f"Added By: {requested_by}",
        (255, 255, 255),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")




@Client.on_message(command("play") 
                   & filters.group
                   & ~filters.edited 
                   & ~filters.forwarded
                   & ~filters.via_bot)
async def play(_, message: Message):

    lel = await message.reply("🔄 **[𝗡𝗼𝗼𝗯𝗲𝘀𝘁𝗥𝗼𝗯𝗼𝘁]«»𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴...**")
    
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "RiZoeL"
    usar = user
    wew = usar.id
    try:
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Add me as admin of yor group first!</b>")
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "**𝗡𝗼𝗼𝗯𝗲𝘀𝘁𝗥𝗼𝗯𝗼𝘁 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 𝗷𝗼𝗶𝗻𝗲𝗱 𝘁𝗵𝗶𝘀 𝗴𝗿𝗼𝘂𝗽 𝗳𝗼𝗿 𝗽𝗹𝗮𝘆 𝗺𝘂𝘀𝗶𝗰 🎵**")

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    await lel.edit(
                        f"</b> 𝗙𝗟𝗢𝗢𝗗 🛑</b> \n\Hey {user.first_name}, assistant userbot couldn't join your group due to heavy join requests. Make sure userbot is not banned in group and try again later!")
    try:
        await USER.get_chat(chid)
    except:
        await lel.edit(
            f"<i>𝗛𝗲𝘆 {user.first_name}, 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 𝘂𝘀𝗲𝗿𝗯𝗼𝘁 𝗶𝘀 𝗻𝗼𝘁 𝗶𝗻 𝘁𝗵𝗶𝘀 𝗰𝗵𝗮𝘁, 𝗮𝘀𝗸 𝗮𝗱𝗺𝗶𝗻 𝘁𝗼 𝘀𝗲𝗻𝗱 /play 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗳𝗼𝗿 𝗳𝗶𝗿𝘀𝘁 𝘁𝗶𝗺𝗲 𝘁𝗼 𝗮𝗱𝗱 𝗶𝘁.</i>")
        return
    
    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"❌ 𝗩𝗶𝗱𝗲𝗼𝘀 𝗹𝗼𝗻𝗴𝗲𝗿 𝘁𝗵𝗮𝗻 {DURATION_LIMIT} 𝗺𝗶𝗻𝘂𝘁𝗲𝘀 𝗮𝗿𝗲𝗻'𝘁 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝘁𝗼 𝗽𝗹𝗮𝘆!"
            )

        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/8c7c5900b3aba128cb3f5.jpg"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="𝗠𝗔𝗫𝗪𝗶𝗡",
                        url="https://t.me/Anurag_1711")
                   
                ]
            ]
        )
        
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)  
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name)) else file_name
        )

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            # print results
            title = results[0]["title"]       
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f'thumb{title}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")
            
            secmul, dur, dur_arr = 1, 0, duration.split(':')
            for i in range(len(dur_arr)-1, -1, -1):
                dur += (int(dur_arr[i]) * secmul)
                secmul *= 60
                
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝗬𝗼𝘂𝗧𝘂𝗯𝗲 🎬",
                            url=f"{url}"),
                        InlineKeyboardButton(
                            text="𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 📥",
                            url=f"{durl}")

                    ]
                ]
            )
        except Exception as e:
            title = "NaN"
            thumb_name = "https://telegra.ph/file/8c7c5900b3aba128cb3f5.jpg"
            duration = "NaN"
            views = "NaN"
            keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="𝗬𝗼𝘂𝗧𝘂𝗯𝗲 🎬",
                                url=f"https://youtube.com")

                        ]
                    ]
                )
        if (dur / 60) > DURATION_LIMIT:
             await lel.edit(f"❌ 𝗩𝗶𝗱𝗲𝗼𝘀 𝗹𝗼𝗻𝗴𝗲𝗿 𝘁𝗵𝗮𝗻 {DURATION_LIMIT} 𝗺𝗶𝗻𝘂𝘁𝗲𝘀 𝗮𝗿𝗲𝗻'𝘁 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝘁𝗼 𝗽𝗹𝗮𝘆!")
             return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)     
        file_path = await converter.convert(youtube.download(url))
    else:
        if len(message.command) < 2:
            return await lel.edit("🧐 **What's the song you want to play?**")
        await lel.edit("🔎**𝗙𝗶𝗻𝗱𝗶𝗻𝗴 𝗦𝗼𝗻𝗴 𝗪𝗮𝗶𝘁...**🎧")
        query = message.text.split(None, 1)[1]
        # print(query)
        await lel.edit("🎵 **𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝗦𝗼𝘂𝗻𝗱...** 🔊")
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print results
            title = results[0]["title"]       
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f'thumb{title}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(':')
            for i in range(len(dur_arr)-1, -1, -1):
                dur += (int(dur_arr[i]) * secmul)
                secmul *= 60
                
        except Exception as e:
            await lel.edit(
                "❌ 𝗦𝗼𝗻𝗴 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱.\n\n𝗧𝗿𝘆 𝗮𝗻𝗼𝘁𝗵𝗲𝗿 𝘀𝗼𝗻𝗴 𝗼𝗿 𝗺𝗮𝘆 𝗯𝗲 𝘀𝗽𝗲𝗹𝗹 𝗶𝘁 𝗽𝗿𝗼𝗽𝗲𝗿𝗹𝘆."
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝗬𝗼𝘂𝗧𝘂𝗯𝗲 🎬",
                            url=f"{url}"),
                        InlineKeyboardButton(
                            text="𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 📥",
                            url=f"{durl}")

                    ]
                ]
            )
        
        if (dur / 60) > DURATION_LIMIT:
             await lel.edit(f"❌ 𝗩𝗶𝗱𝗲𝗼𝘀 𝗹𝗼𝗻𝗴𝗲𝗿 𝘁𝗵𝗮𝗻 {DURATION_LIMIT} 𝗺𝗶𝗻𝘂𝘁𝗲𝘀 𝗮𝗿𝗲𝗻'𝘁 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝘁𝗼 𝗽𝗹𝗮𝘆!")
             return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)  
        file_path = await converter.convert(youtube.download(url))
  
    if message.chat.id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(message.chat.id, file=file_path)
        await message.reply_photo(
        photo="final.png", 
        caption="**🎵 𝗦𝗼𝗻𝗴:** {}\n**🕒 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻:** {} min\n**👤 𝗔𝗱𝗱𝗲𝗱 𝗯𝘆:** {}\n\n**# 𝗤𝘂𝗲𝘂𝗲𝗱 𝗣𝗼𝘀𝗶𝘁𝗶𝗼𝗻:** {}\n\n 𝗡𝗼𝗼𝗯𝗲𝘀𝘁 𝗥𝗼𝗯𝗼𝘁🌻".format(
        title, duration, message.from_user.mention(), position
        ),
        reply_markup=keyboard)
        os.remove("final.png")
        return await lel.delete()
    else:
        callsmusic.pytgcalls.join_group_call(message.chat.id, file_path)
        await message.reply_photo(
        photo="final.png",
        reply_markup=keyboard,
        caption="**🎵 𝗦𝗼𝗻𝗴:** {}\n**🕒 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻:** {} min\n**👤 𝗔𝗱𝗱𝗲𝗱 𝗯𝘆:** {}\n\n**▶️ 𝗡𝗼𝘄 𝗣𝗹𝗮𝘆𝗶𝗻𝗴 𝗮𝘁 `{}`...\n\n 𝗡𝗼𝗼𝗯𝗲𝘀𝘁 𝗥𝗼𝗯𝗼𝘁🌻**".format(
        title, duration, message.from_user.mention(), message.chat.title
        ), )
        os.remove("final.png")
        return await lel.delete()
