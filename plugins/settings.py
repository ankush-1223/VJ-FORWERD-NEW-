# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
import asyncio
from database import Db, db
from script import Script
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .test import get_configs, update_configs, CLIENT, parse_buttons
from .db import connect_user_db

CLIENT = CLIENT()

async def handle_back_button(message, callback_data="settings#main"):
    """Helper function to handle back button consistently"""
    buttons = [[InlineKeyboardButton('⫷ Back', callback_data=callback_data)]]
    await message.edit_text(
        "<b>Operation completed</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r'^settings'))
async def settings_query(bot, query):
    try:
        user_id = query.from_user.id
        i, type = query.data.split("#")
        
        if type == "caption":
            buttons = []
            data = await get_configs(user_id)
            caption = data.get('caption')
            replacements = data.get('replacement_words') or {}
            delete_words = data.get('delete_words') or []

            if caption is None:
                buttons.append([InlineKeyboardButton('✚ Add Caption ✚',
                                                  callback_data="settings#addcaption")])
            else:
                buttons.append([
                    InlineKeyboardButton('👀 See Caption', callback_data="settings#seecaption"),
                    InlineKeyboardButton('🗑️ Delete Caption', callback_data="settings#deletecaption")
                ])
                if replacements:
                    buttons.append([InlineKeyboardButton('🔄 Replace Words',
                                                      callback_data="settings#setreplacement")])
                if delete_words:
                    buttons.append([InlineKeyboardButton('🗑️ Remove Words',
                                                      callback_data="settings#deleteword")])
                buttons.append([InlineKeyboardButton('🔁 Reset Caption Settings',
                                                  callback_data="settings#resetcaption")])

            buttons.append([InlineKeyboardButton('⫷ Back', callback_data="settings#main")])

            await query.message.edit_text(
                "<b><u>CUSTOM CAPTION</u></b>\n\n"
                "<b>You can set a custom caption for videos and documents. By default, the original caption is used.</b>\n\n"
                "<b><u>AVAILABLE FILLINGS:</u></b>\n"
                "- <code>{filename}</code> : Filename\n"
                "- <code>{size}</code> : File size\n"
                "- <code>{caption}</code> : Default caption\n\n"
                "<b>You can also replace or delete specific words from the filename/caption.</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        elif type == "setreplacement":
            try:
                await query.message.delete()
                ask = await bot.ask(query.message.chat.id, 
                    "**Send word to replace in format:**\n`'WORD' 'REPLACEWORD'`\n\n/cancel to abort")
                
                if ask.text == "/cancel":
                    return await handle_back_button(ask, "settings#caption")
                
                match = re.match(r"'(.+)' '(.+)'", ask.text)
                if not match:
                    return await ask.reply("❌ Invalid format. Use `'OLD' 'NEW'`.")
                
                word, replace_word = match.groups()
                data = await get_configs(user_id)
                delete_words = data.get('delete_words', [])
                
                if word in delete_words:
                    return await ask.reply(
                        f"❌ The word '{word}' is in the delete list and cannot be replaced.",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Back', callback_data="settings#caption")]])
                    )
                
                replacements = data.get('replacement_words', {}) or {}
                replacements[word] = replace_word
                await update_configs(user_id, 'replacement_words', replacements)
                await handle_back_button(ask, "settings#caption")
                
            except Exception as e:
                await query.message.reply(f"❌ Error: {str(e)}")
                await handle_back_button(query.message, "settings#caption")

        elif type == "deleteword":
            try:
                await query.message.delete()
                ask = await bot.ask(query.message.chat.id, 
                    "**Send word(s) to delete (space separated)**\n\n/cancel to abort")
                
                if ask.text == "/cancel":
                    return await handle_back_button(ask, "settings#caption")
                
                words = ask.text.strip().split()
                data = await get_configs(user_id)
                delete_words = data.get('delete_words', []) or []
                delete_words.extend(w for w in words if w not in delete_words)
                
                await update_configs(user_id, 'delete_words', delete_words)
                await handle_back_button(ask, "settings#caption")
                
            except Exception as e:
                await query.message.reply(f"❌ Error: {str(e)}")
                await handle_back_button(query.message, "settings#caption")

        elif type == "resetcaption":
            try:
                await update_configs(user_id, 'caption', None)
                await update_configs(user_id, 'replacement_words', None)
                await update_configs(user_id, 'delete_words', None)
                await handle_back_button(query.message, "settings#caption")
            except Exception as e:
                await query.message.reply(f"❌ Error: {str(e)}")
                await handle_back_button(query.message, "settings#caption")

        elif type == "seecaption":
            try:
                data = await get_configs(user_id)
                caption = data.get('caption', 'No caption set')
                replacements = data.get('replacement_words', {})
                delete_words = data.get('delete_words', [])
                
                text = "<b><u>YOUR CAPTION SETTINGS</b></u>\n\n"
                text += "<b>📝 Original Caption:</b>\n<code>{}</code>\n\n".format(caption)
                
                if replacements:
                    text += "<b>🔄 Word Replacements:</b>\n"
                    for old, new in replacements.items():
                        text += f"• <code>{old}</code> → <code>{new}</code>\n"
                    text += "\n"
                
                if delete_words:
                    text += "<b>🗑️ Words to Delete:</b>\n"
                    for word in delete_words:
                        text += f"• <code>{word}</code>\n"
                    text += "\n"
                
                buttons = [
                    [InlineKeyboardButton('🖋️ Edit Caption', callback_data="settings#addcaption")],
                    [InlineKeyboardButton('🔄 Add Replacement', callback_data="settings#setreplacement")],
                    [InlineKeyboardButton('🗑️ Add Delete Word', callback_data="settings#deleteword")],
                    [InlineKeyboardButton('🔁 Reset All', callback_data="settings#resetcaption")],
                    [InlineKeyboardButton('⫷ Back', callback_data="settings#caption")]
                ]
                
                await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
                
            except Exception as e:
                await query.message.reply(f"❌ Error: {str(e)}")
                await handle_back_button(query.message, "settings#caption")

        elif type == "deletecaption":
            try:
                await update_configs(user_id, 'caption', None)
                await handle_back_button(query.message, "settings#caption")
            except Exception as e:
                await query.message.reply(f"❌ Error: {str(e)}")
                await handle_back_button(query.message, "settings#caption")

        elif type == "addcaption":
            try:
                await query.message.delete()
                caption = await bot.ask(query.message.chat.id, 
                    "Send your custom caption\n/cancel - <code>cancel this process</code>")
                
                if caption.text == "/cancel":
                    return await handle_back_button(caption, "settings#caption")
                
                # Validate caption format
                required_keys = {'filename', 'size', 'caption'}
                try:
                    test_format = caption.text.format(filename='', size='', caption='')
                    # Check if all required keys are present
                    if not all(key in caption.text for key in required_keys):
                        return await caption.reply(
                            f"❌ Missing required placeholders. Must include: {', '.join(required_keys)}",
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Back', callback_data="settings#caption")]])
                        )
                except KeyError as e:
                    return await caption.reply(
                        f"❌ Invalid placeholder {e}. Use only: {', '.join(required_keys)}",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Back', callback_data="settings#caption")]])
                    )
                
                await update_configs(user_id, 'caption', caption.text)
                await handle_back_button(caption, "settings#caption")
                
            except Exception as e:
                await query.message.reply(f"❌ Error: {str(e)}")
                await handle_back_button(query.message, "settings#caption")

        elif type == "button":
            try:
                buttons = []
                data = await get_configs(user_id)
                button = data.get('button')
                
                if button is None:
                    buttons.append([InlineKeyboardButton('✚ Add Button ✚', 
                                  callback_data="settings#addbutton")])
                else:
                    buttons.append([
                        InlineKeyboardButton('👀 See Button', callback_data="settings#seebutton"),
                        InlineKeyboardButton('🗑️ Remove Button', callback_data="settings#deletebutton")
                    ])
                
                buttons.append([InlineKeyboardButton('⫷ Back', callback_data="settings#main")])
                
                await query.message.edit_text(
                    "<b><u>CUSTOM BUTTON</b></u>\n\n"
                    "<b>You can set an inline button to messages.</b>\n\n"
                    "<b><u>FORMAT:</b></u>\n"
                    "`[Forward bot][buttonurl:https://t.me/mychannelurl]`\n",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                
            except Exception as e:
                await query.message.reply(f"❌ Error: {str(e)}")
                await handle_back_button(query.message, "settings#main")

    except Exception as e:
        await query.message.reply(f"❌ An error occurred: {str(e)}")
        await handle_back_button(query.message, "settings#main")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
