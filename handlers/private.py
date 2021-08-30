from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_NAME as bn
from helpers.filters import other_filters2


@Client.on_message(other_filters2)
async def start(_, message: Message):
    
    await message.reply_text(
        f"""**Hey, I'm {bn} 🎵

I'm Private music of @Anurag_1711 For group's voice call. Developed by [🌻𝗠𝗔𝗫𝗪𝗶𝗡](https://t.me/Anurag_1711).

If you want to add this Bot in your group Contact @Anurag_1711**
        """,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🌻𝗠𝗔𝗫𝗪𝗶𝗡", url="https://t.me/Anurag_1711")
                  ],[ 
                    InlineKeyboardButton(
                        "🌻𝗚𝗥𝗢𝗨𝗣", url="https://t.me/TheDenominators_xD"
                    )]
            ]
        ),
     disable_web_page_preview=True
    )

@Client.on_message(filters.command("start") & ~filters.private & ~filters.channel)
async def gstart(_, message: Message):
      await message.reply_text("""**𝗡𝗼𝗼𝗯𝗲𝘀𝘁 𝗥𝗼𝗯𝗼𝘁 𝗢𝗻𝗹𝗶𝗻𝗲✅**""",
      reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🌻𝗔𝗕𝗢𝗨𝗧 𝗠𝗔𝗫𝗪𝗶𝗡", url="https://t.me/ABOUTMAXWiN")
                ]
            ]
        )
   )


