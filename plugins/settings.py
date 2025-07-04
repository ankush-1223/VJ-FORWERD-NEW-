# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio 
import logging
from database import Db, db
from script import Script
from pyrogram import Client, filters
from .test import get_configs, update_configs, CLIENT, parse_buttons
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .db import connect_user_db
import re
from pyrogram.errors import MessageNotModified


# --- FIX START: safe_edit_text helper ---
async def safe_edit_text(message, text, reply_markup=None, **kwargs):
    try:
        if message.text != text or message.reply_markup != reply_markup:
            await message.edit_text(text, reply_markup=reply_markup, **kwargs)
    except MessageNotModified:
        pass
# --- FIX END ---


logger = logging.getLogger(__name__)
CLIENT = CLIENT()

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

async def handle_error(message, error, back_to="settings#main"):
    """Handle errors in settings operations"""
    error_msg = f"❌ Error: {str(error)}"
    logger.error(f"Settings error: {error}", exc_info=True)
    try:
        await message.reply(error_msg)
        await handle_back_button(message, back_to)
    except Exception as e:
        logger.error(f"Error in handle_error: {e}", exc_info=True)

@Client.on_message(filters.command('settings'))
async def settings(client, message):
    try:
        await message.reply_text(
            "<b>Hᴇʀᴇ Is Tʜᴇ Sᴇᴛᴛɪɴɢs Pᴀɴᴇʟ⚙\n\nᴄʜᴀɴɢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ᴀs ʏᴏᴜʀ ᴡɪsʜ 👇</b>",
            reply_markup=main_buttons()
        )
    except Exception as e:
        logger.error(f"Error in settings command: {e}", exc_info=True)
        await message.reply("❌ An error occurred while opening settings.")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

async def handle_back_button(message, callback_data="settings#main"):
    """Handle back button actions consistently"""
    try:
        buttons = [[InlineKeyboardButton('⫷ Back', callback_data=callback_data)]]
        await message.reply_text(
            "<b>Operation completed. Use back button to return.</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logger.error(f"Error in handle_back_button: {e}", exc_info=True)

@Client.on_callback_query(filters.regex(r'^settings'))
async def settings_query(bot, query):
    try:
        # Use wait_for instead of timeout context manager
        await asyncio.wait_for(process_settings_query(bot, query), timeout=30)
    except asyncio.TimeoutError:
        logger.warning(f"Settings operation timed out for user {query.from_user.id}")
        await safe_edit_text(query.message, 
            "⏰ Operation timed out. Please try again.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⫷ Back', callback_data="settings#main")]])
        )
    except Exception as e:
        logger.error(f"Error in settings_query: {e}", exc_info=True)
        await handle_error(query.message, e)

async def process_settings_query(bot, query):
    user_id = query.from_user.id
    i, type = query.data.split("#")
    buttons = [[InlineKeyboardButton('⫷ Back', callback_data="settings#main")]]
    
    if type=="main":
        await safe_edit_text(query.message, 
            "<b>Hᴇʀᴇ Is Tʜᴇ Sᴇᴛᴛɪɴɢs Pᴀɴᴇʟ⚙\n\nᴄʜᴀɴɢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ᴀs ʏᴏᴜʀ ᴡɪsʜ 👇</b>",
            reply_markup=main_buttons())
    elif type=="extra":
        await safe_edit_text(query.message, 
            "<b>Hᴇʀᴇ Is Tʜᴇ Exᴛʀᴀ Sᴇᴛᴛɪɴɢs Pᴀɴᴇʟ⚙</b>",
            reply_markup=extra_buttons())
    elif type=="bots":
        buttons = [] 
        _bot = await db.get_bot(user_id)
        usr_bot = await db.get_userbot(user_id)
        if _bot is not None:
            buttons.append([InlineKeyboardButton(_bot['name'],
                             callback_data=f"settings#editbot")])
        else:
            buttons.append([InlineKeyboardButton('✚ Add bot ✚', 
                             callback_data="settings#addbot")])
        if usr_bot is not None:
            buttons.append([InlineKeyboardButton(usr_bot['name'],
                             callback_data=f"settings#edituserbot")])
        else:
            buttons.append([InlineKeyboardButton('✚ Add User bot ✚', 
                             callback_data="settings#adduserbot")])
        buttons.append([InlineKeyboardButton('back', 
                          callback_data="settings#main")])
        await safe_edit_text(query.message, 
            "<b><u>My Bots</b></u>\n\n<b>You can manage your bots in here</b>",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="addbot":
        await query.message.delete()
        bot = await CLIENT.add_bot(bot, query)
        if bot != True: return
        await query.message.reply_text(
            "<b>bot token successfully added to db</b>",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="adduserbot":
        await query.message.delete()
        user = await CLIENT.add_session(bot, query)
        if user != True: return
        await query.message.reply_text(
            "<b>session successfully added to db</b>",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="channels":
        buttons = []
        channels = await db.get_user_channels(user_id)
        for channel in channels:
            buttons.append([InlineKeyboardButton(f"{channel['title']}",
                             callback_data=f"settings#editchannels_{channel['chat_id']}")])
        buttons.append([InlineKeyboardButton('✚ Add Channel ✚', 
                          callback_data="settings#addchannel")])
        buttons.append([InlineKeyboardButton('back', 
                          callback_data="settings#main")])
        await safe_edit_text(query.message,  
            "<b><u>My Channels</b></u>\n\n<b>you can manage your target chats in here</b>",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="addchannel":  
        await query.message.delete()
        chat_ids = await bot.ask(chat_id=query.from_user.id, text="<b>❪ SET TARGET CHAT ❫\n\nForward a message from Your target chat\n/cancel - cancel this process</b>")
        if chat_ids.text=="/cancel":
            return await chat_ids.reply_text(
                      "<b>process canceled</b>",
                      reply_markup=InlineKeyboardMarkup(buttons))
        elif not chat_ids.forward_date:
            return await chat_ids.reply("**This is not a forward message**")
        else:
            chat_id = chat_ids.forward_from_chat.id
            title = chat_ids.forward_from_chat.title
            username = chat_ids.forward_from_chat.username
            username = "@" + username if username else "private"
        chat = await db.add_channel(user_id, chat_id, title, username)
        await query.message.reply_text(
            "<b>Successfully updated</b>" if chat else "<b>This channel already added</b>",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="editbot": 
        bot = await db.get_bot(user_id)
        TEXT = Script.BOT_DETAILS if bot['is_bot'] else Script.USER_DETAILS
        buttons = [[InlineKeyboardButton('❌ Remove ❌', callback_data=f"settings#removebot")
                  ],
                  [InlineKeyboardButton('back', callback_data="settings#bots")]]
        await safe_edit_text(query.message, 
            TEXT.format(bot['name'], bot['id'], bot['username']),
            reply_markup=InlineKeyboardMarkup(buttons))
        
    elif type=="edituserbot": 
        bot = await db.get_userbot(user_id)
        TEXT = Script.USER_DETAILS
        buttons = [[InlineKeyboardButton('❌ Remove ❌', callback_data=f"settings#removeuserbot")
                  ],
                  [InlineKeyboardButton('back', callback_data="settings#bots")]]
        await safe_edit_text(query.message, 
            TEXT.format(bot['name'], bot['id'], bot['username']),
            reply_markup=InlineKeyboardMarkup(buttons))
        
    elif type=="removebot":
        await db.remove_bot(user_id)
        await safe_edit_text(query.message, 
            "<b>successfully updated</b>",
            reply_markup=InlineKeyboardMarkup(buttons))
        
    elif type=="removeuserbot":
        await db.remove_userbot(user_id)
        await safe_edit_text(query.message, 
            "<b>successfully updated</b>",
            reply_markup=InlineKeyboardMarkup(buttons))
        
    elif type.startswith("editchannels"): 
        chat_id = type.split('_')[1]
        chat = await db.get_channel_details(user_id, chat_id)
        buttons = [[InlineKeyboardButton('❌ Remove ❌', callback_data=f"settings#removechannel_{chat_id}")
                  ],
                  [InlineKeyboardButton('back', callback_data="settings#channels")]]
        await safe_edit_text(query.message, 
            f"<b><u>📄 CHANNEL DETAILS</b></u>\n\n<b>- TITLE:</b> <code>{chat['title']}</code>\n<b>- CHANNEL ID: </b> <code>{chat['chat_id']}</code>\n<b>- USERNAME:</b> {chat['username']}",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type.startswith("removechannel"):
        chat_id = type.split('_')[1]
        await db.remove_channel(user_id, chat_id)
        await safe_edit_text(query.message, 
            "<b>successfully updated</b>",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="caption":
        buttons = []
        data = await get_configs(user_id)
        caption = data.get('caption')

        # Main caption buttons
        if caption is None:
            buttons.append([InlineKeyboardButton('✚ Add Caption ✚',
                                              callback_data="settings#addcaption")])
        else:
            buttons.append([
                InlineKeyboardButton('👀 See Caption', callback_data="settings#seecaption"),
                InlineKeyboardButton('🗑️ Delete Caption', callback_data="settings#deletecaption")
            ])

        # Separate buttons for each feature
        buttons.append([InlineKeyboardButton('🔄 Add Word Replacement', 
                                          callback_data="settings#setreplacement")])
        buttons.append([InlineKeyboardButton('🗑️ Add Words to Delete', 
                                          callback_data="settings#deleteword")])
        buttons.append([InlineKeyboardButton('🔁 Reset All Settings', 
                                          callback_data="settings#resetcaption")])
        buttons.append([InlineKeyboardButton('⫷ Back', callback_data="settings#main")])

        await safe_edit_text(query.message, 
            "<b><u>CUSTOM CAPTION</u></b>\n\n"
            "<b>You can customize your captions in multiple ways:</b>\n\n"
            "1️⃣ <b>Set Custom Caption</b>\n"
            "   Use placeholders: <code>{filename}</code>, <code>{size}</code>, <code>{caption}</code>\n\n"
            "2️⃣ <b>Word Replacements</b>\n"
            "   Replace specific words in captions\n\n"
            "3️⃣ <b>Delete Words</b>\n"
            "   Remove specific words from captions\n\n"
            "<i>Click any button below to get started</i>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif type=="seecaption":   
        try:
            data = await get_configs(user_id)
            caption = data.get('caption', 'No caption set')
            replacements = data.get('replacement_words', {}) or {}
            delete_words = data.get('delete_words', []) or []
            
            text = "<b><u>YOUR CAPTION SETTINGS</b></u>\n\n"
            
            # Show Original Caption
            text += "<b>📝 Original Caption:</b>\n"
            text += f"<code>{caption}</code>\n\n"
            
            # Show Word Replacements
            text += "<b>🔄 Word Replacements:</b>\n"
            if replacements:
                for old, new in replacements.items():
                    text += f"• <code>{old}</code> → <code>{new}</code>\n"
            else:
                text += "No replacements set\n"
            text += "\n"
            
            # Show Words to Delete
            text += "<b>🗑️ Words to Delete:</b>\n"
            if delete_words:
                for word in delete_words:
                    text += f"• <code>{word}</code>\n"
            else:
                text += "No words set for deletion\n"
            text += "\n"
            
            # Show Example with all changes applied
            if caption != 'No caption set':
                text += "<b>📋 Example Output:</b>\n"
                try:
                    # First apply the caption template
                    example = caption.format(
                        filename="example.mp4",
                        size="100MB",
                        caption="Original caption"
                    )
                    
                    # Then apply all replacements
                    for old, new in replacements.items():
                        example = example.replace(old, new)
                    
                    # Finally remove all deleted words
                    for word in delete_words:
                        example = example.replace(word, "")
                    
                    # Clean up any double spaces that might have been created
                    example = ' '.join(example.split())
                    
                    text += f"<code>{example}</code>\n\n"
                except Exception as e:
                    text += f"<i>Could not generate example: {str(e)}</i>\n\n"
            
            buttons = [
                [InlineKeyboardButton('🖋️ Edit Caption', callback_data="settings#addcaption")],
                [InlineKeyboardButton('🔄 Add Replacement', callback_data="settings#setreplacement")],
                [InlineKeyboardButton('🗑️ Add Delete Word', callback_data="settings#deleteword")],
                [InlineKeyboardButton('🔁 Reset All', callback_data="settings#resetcaption")],
                [InlineKeyboardButton('⫷ Back', callback_data="settings#caption")]
            ]
            
            try:
                await safe_edit_text(query.message, text, reply_markup=InlineKeyboardMarkup(buttons))
            except MessageNotModified:
                # If message wasn't modified, just ignore the error
                pass
            
        except Exception as e:
            logger.error(f"Error in seecaption: {e}", exc_info=True)
            await query.message.reply(f"❌ Error: {str(e)}")
            await handle_back_button(query.message, "settings#caption")

    elif type=="deletecaption":
        try:
            await update_configs(user_id, 'caption', None)
            await handle_back_button(query.message, "settings#caption")
        except Exception as e:
            await query.message.reply(f"❌ Error: {str(e)}")
            await handle_back_button(query.message, "settings#caption")

    elif type=="addcaption":
        try:
            await query.message.delete()
            caption = await bot.ask(query.message.chat.id, 
                "Send your custom caption\n\n<b>Available placeholders:</b>\n"
                "- <code>{filename}</code> : Original filename\n"
                "- <code>{size}</code> : File size\n"
                "- <code>{caption}</code> : Original caption\n\n"
                "You can use any or all of these placeholders.\n"
                "/cancel - <code>cancel this process</code>")
            
            if caption.text == "/cancel":
                return await handle_back_button(caption, "settings#caption")
            
            # More flexible validation - allow any text with optional placeholders
            try:
                # Try to format with empty values for any placeholders used
                test_format = caption.text.format(
                    filename='', 
                    size='', 
                    caption=''
                )
            except KeyError as e:
                return await caption.reply(
                    f"❌ Invalid placeholder {e}. You can only use: filename, size, caption",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⫷ Back', callback_data="settings#caption")]])
                )
            
            await update_configs(user_id, 'caption', caption.text)
            await handle_back_button(caption, "settings#caption")
            
        except Exception as e:
            await query.message.reply(f"❌ Error: {str(e)}")
            await handle_back_button(query.message, "settings#caption")

    elif type=="setreplacement":
        try:
            await query.message.delete()
            ask = await bot.ask(query.message.chat.id, 
                "Send word to replace in this format:\n"
                "<code>'OLD WORD' 'NEW WORD'</code>\n\n"
                "Example: <code>'movie' 'film'</code>\n\n"
                "/cancel to abort")
            
            if ask.text == "/cancel":
                return await handle_back_button(ask, "settings#caption")
            
            match = re.match(r"'(.+)' '(.+)'", ask.text)
            if not match:
                return await ask.reply(
                    "❌ Invalid format. Please use: <code>'OLD WORD' 'NEW WORD'</code>",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⫷ Back', callback_data="settings#caption")]])
                )
            
            word, replace_word = match.groups()
            data = await get_configs(user_id)
            delete_words = data.get('delete_words', [])
            
            if word in delete_words:
                return await ask.reply(
                    f"❌ The word '{word}' is in the delete list and cannot be replaced.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⫷ Back', callback_data="settings#caption")]])
                )
            
            replacements = data.get('replacement_words', {}) or {}
            replacements[word] = replace_word
            await update_configs(user_id, 'replacement_words', replacements)
            
            # Keep original feature with "See Updated Caption" button
            await ask.reply(
                f"✅ Successfully added replacement:\n<code>{word}</code> → <code>{replace_word}</code>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('👀 See Updated Caption', callback_data="settings#seecaption")]])
            )
            
        except Exception as e:
            await query.message.reply(f"❌ Error: {str(e)}")
            await handle_back_button(query.message, "settings#caption")

    elif type=="deleteword":
        try:
            await query.message.delete()
            ask = await bot.ask(query.message.chat.id, 
                "Send word(s) to delete from captions\n\n"
                "You can send multiple words separated by spaces\n"
                "Example: <code>movie film video</code>\n\n"
                "/cancel to abort")
            
            if ask.text == "/cancel":
                return await handle_back_button(ask, "settings#caption")
            
            words = ask.text.strip().split()
            if not words:
                return await ask.reply(
                    "❌ Please send at least one word to delete",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⫷ Back', callback_data="settings#caption")]])
                )
            
            data = await get_configs(user_id)
            delete_words = data.get('delete_words', []) or []
            new_words = [w for w in words if w not in delete_words]
            delete_words.extend(new_words)
            
            # Check if any words are in replacements
            replacements = data.get('replacement_words', {}) or {}
            conflicting_words = [word for word in new_words if word in replacements]
            if conflicting_words:
                return await ask.reply(
                    f"❌ The following words are in your replacements and cannot be deleted: {', '.join(conflicting_words)}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⫷ Back', callback_data="settings#caption")]])
                )
            
            await update_configs(user_id, 'delete_words', delete_words)
            
            # Keep original feature with "See Updated Caption" button
            await ask.reply(
                f"✅ Successfully added {len(new_words)} word(s) to delete list",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('👀 See Updated Caption', callback_data="settings#seecaption")]])
            )
            
        except Exception as e:
            await query.message.reply(f"❌ Error: {str(e)}")
            await handle_back_button(query.message, "settings#caption")

    elif type=="resetcaption":
        try:
            # Reset all caption settings
            await update_configs(user_id, 'caption', None)
            await update_configs(user_id, 'replacement_words', {})
            await update_configs(user_id, 'delete_words', [])
            
            # Show the updated empty caption view
            await safe_edit_text(query.message, 
                "<b>✅ All caption settings have been reset</b>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('👀 See Caption Settings', callback_data="settings#seecaption")]])
            )
        except Exception as e:
            await query.message.reply(f"❌ Error: {str(e)}")
            await handle_back_button(query.message, "settings#caption")

    elif type=="button":
        buttons = []
        button = (await get_configs(user_id))['button']
        if button is None:
            buttons.append([InlineKeyboardButton('✚ Add Button ✚', 
                                  callback_data="settings#addbutton")])
        else:
            buttons.append([InlineKeyboardButton('👀 See Button', 
                                  callback_data="settings#seebutton")])
            buttons[-1].append(InlineKeyboardButton('🗑️ Remove Button ', 
                                  callback_data="settings#deletebutton"))
        buttons.append([InlineKeyboardButton('back', 
                                  callback_data="settings#main")])
        await safe_edit_text(query.message, 
            "<b><u>CUSTOM BUTTON</b></u>\n\n<b>You can set a inline button to messages.</b>\n\n<b><u>FORMAT:</b></u>\n`[Forward bot][buttonurl:https://t.me/mychannelurl]`\n",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="addbutton":
        await query.message.delete()
        ask = await bot.ask(user_id, text="**Send your custom button.\n\nFORMAT:**\n`[forward bot][buttonurl:https://t.me/url]`\n")
        button = parse_buttons(ask.text.html)
        if not button:
            return await ask.reply("**INVALID BUTTON**")
        await update_configs(user_id, 'button', ask.text.html)
        await ask.reply("**Successfully button added**",
                reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="seebutton":
        button = (await get_configs(user_id))['button']
        button = parse_buttons(button, markup=False)
        button.append([InlineKeyboardButton("back", "settings#button")])
        await safe_edit_text(query.message, 
            "**YOUR CUSTOM BUTTON**",
            reply_markup=InlineKeyboardMarkup(button))

    elif type=="deletebutton":
        await update_configs(user_id, 'button', None)
        await safe_edit_text(query.message, 
            "**Successfully button deleted**",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="database":
        buttons = []
        db_uri = (await get_configs(user_id))['db_uri']
        if db_uri is None:
            buttons.append([InlineKeyboardButton('✚ Add Mongo Url ', 
                                  callback_data="settings#addurl")])
        else:
            buttons.append([InlineKeyboardButton('👀 See Url', 
                                  callback_data="settings#seeurl")])
            buttons[-1].append(InlineKeyboardButton('❌ Remove Url ', 
                                  callback_data="settings#deleteurl"))
        buttons.append([InlineKeyboardButton('back', 
                                  callback_data="settings#main")])
        await safe_edit_text(query.message, 
            "<b><u>DATABASE</u>\n\nDatabase is required for store your duplicate messages permenant. other wise stored duplicate media may be disappeared when after bot restart.</b>",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="addurl":
        await query.message.delete()
        uri = await bot.ask(user_id, "<b>please send your mongodb url.</b>\n\n<i>get your Mongodb url from [MangoDb](https://mongodb.com)</i>", disable_web_page_preview=True)
        if uri.text=="/cancel":
            return await uri.reply_text(
                      "<b>process canceled !</b>",
                      reply_markup=InlineKeyboardMarkup(buttons))
        if not uri.text.startswith("mongodb+srv://") and not uri.text.endswith("majority"):
            return await uri.reply("<b>Invalid Mongodb Url</b>",
                       reply_markup=InlineKeyboardMarkup(buttons))
        connect, udb = await connect_user_db(user_id, uri.text, "test")
        if connect:
            await udb.drop_all()
            await udb.close()
        else:
            return await uri.reply("<b>Invalid Mongodb Url Cant Connect With This Uri</b>",
                      reply_markup=InlineKeyboardMarkup(buttons))
        await update_configs(user_id, 'db_uri', uri.text)
        await uri.reply("**Successfully database url added**",
                reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="seeurl":
        db_uri = (await get_configs(user_id))['db_uri']
        await query.answer(f"DATABASE URL: {db_uri}", show_alert=True)

    elif type=="deleteurl":
        await update_configs(user_id, 'db_uri', None)
        await safe_edit_text(query.message, 
            "**Successfully your database url deleted**",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type=="filters":
        await safe_edit_text(query.message, 
            "<b><u>💠 CUSTOM FILTERS 💠</b></u>\n\n**configure the type of messages which you want forward**",
            reply_markup=await filters_buttons(user_id))

    elif type=="nextfilters":
        await query.edit_message_reply_markup( 
            reply_markup=await next_filters_buttons(user_id))

    elif type.startswith("updatefilter"):
        i, key, value = type.split('-')
        if value=="True":
            await update_configs(user_id, key, False)
        else:
            await update_configs(user_id, key, True)
        if key in ['poll', 'protect', 'voice', 'animation', 'sticker', 'duplicate']:
            return await query.edit_message_reply_markup(
               reply_markup=await next_filters_buttons(user_id)) 
        await query.edit_message_reply_markup(
            reply_markup=await filters_buttons(user_id))

    elif type.startswith("file_size"):
        settings = await get_configs(user_id)
        size = settings.get('min_size', 0)
        await safe_edit_text(query.message, 
            f'<b><u>SIZE LIMIT</b></u><b>\n\nyou can set file Minimum size limit to forward\n\nfiles with greater than `{size} MB` will forward</b>',
            reply_markup=size_button(size))
        
    elif type.startswith("maxfile_size"):
        settings = await get_configs(user_id)
        size = settings.get('max_size', 0)
        await safe_edit_text(query.message, 
            f'<b><u>Max SIZE LIMIT</b></u><b>\n\nyou can set file Maximum size limit to forward\n\nfiles with less than `{size} MB` will forward</b>',
            reply_markup=maxsize_button(size))

    elif type.startswith("update_size"):
        size = int(query.data.split('-')[1])
        if 0 < size > 4000:
            return await query.answer("size limit exceeded", show_alert=True)
        await update_configs(user_id, 'min_size', size)
        i, limit = size_limit((await get_configs(user_id))['size_limit'])
        await safe_edit_text(query.message, 
            f'<b><u>SIZE LIMIT</b></u><b>\n\nyou can set file Minimum size limit to forward\n\nfiles with greater than `{size} MB` will forward</b>',
            reply_markup=size_button(size))
        
    elif type.startswith("maxupdate_size"):
        size = int(query.data.split('-')[1])
        if 0 < size > 4000:
            return await query.answer("size limit exceeded", show_alert=True)
        await update_configs(user_id, 'max_size', size)
        i, limit = size_limit((await get_configs(user_id))['size_limit'])
        await safe_edit_text(query.message, 
            f'<b><u>Max SIZE LIMIT</b></u><b>\n\nyou can set file Maximum size limit to forward\n\nfiles with less than `{size} MB` will forward</b>',
            reply_markup=maxsize_button(size))

    elif type.startswith('update_limit'):
        i, limit, size = type.split('-')
        limit, sts = size_limit(limit)
        await update_configs(user_id, 'size_limit', limit) 
        await safe_edit_text(query.message, 
            f'<b><u>SIZE LIMIT</b></u><b>\n\nyou can set file size limit to forward\n\nStatus: files with {sts} `{size} MB` will forward</b>',
            reply_markup=size_button(int(size)))

    elif type == "add_extension":
        await query.message.delete() 
        ext = await bot.ask(user_id, text="**please send your extensions (seperete by space)**")
        if ext.text == '/cancel':
            return await ext.reply_text(
                       "<b>process canceled</b>",
                       reply_markup=InlineKeyboardMarkup(buttons))
        extensions = ext.text.split(" ")
        extension = (await get_configs(user_id))['extension']
        if extension:
            for extn in extensions:
                extension.append(extn)
        else:
            extension = extensions
        await update_configs(user_id, 'extension', extension)
        buttons = []
        buttons.append([InlineKeyboardButton('back', 
                                  callback_data="settings#get_extension")])
        await ext.reply_text(
            f"**successfully updated**",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type == "get_extension":
        extensions = (await get_configs(user_id))['extension']
        btn = []
        text = ""
        if extensions:
            text += "**🕹 Extensions**"
            for ext in extensions:
                text += f"\n<code>-{ext}</code>"
        else:
            text += "** No Extensions Here**"
        btn.append([InlineKeyboardButton('✚ Add', 'settings#add_extension')])
        btn.append([InlineKeyboardButton('Remove All', 'settings#rmve_all_extension')])
        btn.append([InlineKeyboardButton('back', 'settings#extra')])
        await safe_edit_text(query.message, 
            text=f"<b><u>EXTENSIONS</u></b>\n\n**Files with these extiontions will not forward**\n\n{text}",
            reply_markup=InlineKeyboardMarkup(btn))

    elif type == "rmve_all_extension":
        await update_configs(user_id, 'extension', None)
        buttons = []
        buttons.append([InlineKeyboardButton('back', 
                                  callback_data="settings#get_extension")])
        await safe_edit_text(query.message, text="**successfully deleted**",
                                       reply_markup=InlineKeyboardMarkup(buttons))
    elif type == "add_keyword":
        await query.message.delete()
        ask = await bot.ask(user_id, text="**please send the keywords (seperete by space Like:- English 1080p Hdrip)**")
        if ask.text == '/cancel':
            return await ask.reply_text(
                       "<b>process canceled</b>",
                       reply_markup=InlineKeyboardMarkup(buttons))
        keywords = ask.text.split(" ")
        keyword = (await get_configs(user_id))['keywords']
        if keyword:
            for word in keywords:
                keyword.append(word)
        else:
            keyword = keywords
        await update_configs(user_id, 'keywords', keyword)
        buttons = []
        buttons.append([InlineKeyboardButton('back', 
                                  callback_data="settings#get_keyword")])
        await ask.reply_text(
            f"**successfully updated**",
            reply_markup=InlineKeyboardMarkup(buttons))

    elif type == "get_keyword":
        keywords = (await get_configs(user_id))['keywords']
        btn = []
        text = ""
        if keywords:
            text += "**🔖 Keywords:**"
            for key in keywords:
                text += f"\n<code>-{key}</code>"
        else:
            text += "**You didn't Added Any Keywords**"
        btn.append([InlineKeyboardButton('✚ Add', 'settings#add_keyword')])
        btn.append([InlineKeyboardButton('Remove all', 'settings#rmve_all_keyword')])
        btn.append([InlineKeyboardButton('Back', 'settings#extra')])
        await safe_edit_text(query.message, 
            text=f"<b><u>Keywords</u></b>\n\n**Files with these keywords in file name only forwad**\n\n{text}",
            reply_markup=InlineKeyboardMarkup(btn))

    elif type == "rmve_all_keyword":
        await update_configs(user_id, 'keywords', None)
        buttons = []
        buttons.append([InlineKeyboardButton('back', 
                                  callback_data="settings#get_keyword")])
        await safe_edit_text(query.message, text="**successfully deleted All Keywords**",
                                       reply_markup=InlineKeyboardMarkup(buttons))
    elif type.startswith("alert"):
        alert = type.split('_')[1]
        await query.answer(alert, show_alert=True)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

def extra_buttons():
   buttons = [[
       InlineKeyboardButton('💾 Mɪɴ Sɪᴢᴇ Lɪᴍɪᴛ',
                    callback_data=f'settings#file_size')
       ],[
       InlineKeyboardButton('💾 Mᴀx Sɪᴢᴇ Lɪᴍɪᴛ',
                    callback_data=f'settings#maxfile_size ')
       ],[
       InlineKeyboardButton('🚥 Keywords',
                    callback_data=f'settings#get_keyword'),
       InlineKeyboardButton('🕹 Extensions',
                    callback_data=f'settings#get_extension')
       ],[
       InlineKeyboardButton('⫷ Bᴀᴄᴋ',
                    callback_data=f'settings#main')
       ]]
   return InlineKeyboardMarkup(buttons)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

def main_buttons():
  buttons = [[
       InlineKeyboardButton('🤖 Bᴏᴛs',
                    callback_data=f'settings#bots'),
       InlineKeyboardButton('🏷 Cʜᴀɴɴᴇʟs',
                    callback_data=f'settings#channels')
       ],[
       InlineKeyboardButton('🖋️ Cᴀᴘᴛɪᴏɴ',
                    callback_data=f'settings#caption'),
       InlineKeyboardButton('⏹ Bᴜᴛᴛᴏɴ',
                    callback_data=f'settings#button')
       ],[
       InlineKeyboardButton('🕵‍♀ Fɪʟᴛᴇʀs 🕵‍♀',
                    callback_data=f'settings#filters'),
       InlineKeyboardButton('🗃 MᴏɴɢᴏDB',
                    callback_data=f'settings#database')
       ],[
       InlineKeyboardButton('Exᴛʀᴀ Sᴇᴛᴛɪɴɢs 🧪',
                    callback_data=f'settings#extra')
       ],[
       InlineKeyboardButton('⫷ Bᴀᴄᴋ',
                    callback_data=f'help')
       ]]
  return InlineKeyboardMarkup(buttons)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

def size_limit(limit):
   if str(limit) == "None":
      return None, ""
   elif str(limit) == "True":
      return True, "more than"
   else:
      return False, "less than"

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

def extract_btn(datas):
    i = 0
    btn = []
    if datas:
       for data in datas:
         if i >= 3:
            i = 0
         if i == 0:
            btn.append([InlineKeyboardButton(data, f'settings#alert_{data}')])
            i += 1
            continue
         elif i > 0:
            btn[-1].append(InlineKeyboardButton(data, f'settings#alert_{data}'))
            i += 1
    return btn 

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

def maxsize_button(size):
  buttons = [[
       InlineKeyboardButton('💾 Max Size Limit',
                    callback_data=f'noth')
       ],[
       InlineKeyboardButton('+1',
                    callback_data=f'settings#maxupdate_size-{size + 1}'),
       InlineKeyboardButton('-1',
                    callback_data=f'settings#maxupdate_size_-{size - 1}')
       ],[
       InlineKeyboardButton('+5',
                    callback_data=f'settings#maxupdate_size-{size + 5}'),
       InlineKeyboardButton('-5',
                    callback_data=f'settings#maxupdate_size_-{size - 5}')
       ],[
       InlineKeyboardButton('+10',
                    callback_data=f'settings#maxupdate_size-{size + 10}'),
       InlineKeyboardButton('-10',
                    callback_data=f'settings#maxupdate_size_-{size - 10}')
       ],[
       InlineKeyboardButton('+50',
                    callback_data=f'settings#maxupdate_size-{size + 50}'),
       InlineKeyboardButton('-50',
                    callback_data=f'settings#maxupdate_size_-{size - 50}')
       ],[
       InlineKeyboardButton('+100',
                    callback_data=f'settings#maxupdate_size-{size + 100}'),
       InlineKeyboardButton('-100',
                    callback_data=f'settings#maxupdate_size_-{size - 100}')
       ],[
       InlineKeyboardButton('back',
                    callback_data="settings#extra")
     ]]
  return InlineKeyboardMarkup(buttons)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

def size_button(size):
  buttons = [[
       InlineKeyboardButton('💾 Min Size Limit',
                    callback_data=f'noth')
       ],[
       InlineKeyboardButton('+1',
                    callback_data=f'settings#update_size-{size + 1}'),
       InlineKeyboardButton('-1',
                    callback_data=f'settings#update_size_-{size - 1}')
       ],[
       InlineKeyboardButton('+5',
                    callback_data=f'settings#update_size-{size + 5}'),
       InlineKeyboardButton('-5',
                    callback_data=f'settings#update_size_-{size - 5}')
       ],[
       InlineKeyboardButton('+10',
                    callback_data=f'settings#update_size-{size + 10}'),
       InlineKeyboardButton('-10',
                    callback_data=f'settings#update_size_-{size - 10}')
       ],[
       InlineKeyboardButton('+50',
                    callback_data=f'settings#update_size-{size + 50}'),
       InlineKeyboardButton('-50',
                    callback_data=f'settings#update_size_-{size - 50}')
       ],[
       InlineKeyboardButton('+100',
                    callback_data=f'settings#update_size-{size + 100}'),
       InlineKeyboardButton('-100',
                    callback_data=f'settings#update_size_-{size - 100}')
       ],[
       InlineKeyboardButton('back',
                    callback_data="settings#extra")
     ]]
  return InlineKeyboardMarkup(buttons)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

async def filters_buttons(user_id):
  filter = await get_configs(user_id)
  filters = filter['filters']
  buttons = [[
       InlineKeyboardButton('🏷️ Forward tag',
                    callback_data=f'settings_#updatefilter-forward_tag-{filter["forward_tag"]}'),
       InlineKeyboardButton('✅' if filter['forward_tag'] else '❌',
                    callback_data=f'settings#updatefilter-forward_tag-{filter["forward_tag"]}')
       ],[
       InlineKeyboardButton('🖍️ Texts',
                    callback_data=f'settings_#updatefilter-text-{filters["text"]}'),
       InlineKeyboardButton('✅' if filters['text'] else '❌',
                    callback_data=f'settings#updatefilter-text-{filters["text"]}')
       ],[
       InlineKeyboardButton('📁 Documents',
                    callback_data=f'settings_#updatefilter-document-{filters["document"]}'),
       InlineKeyboardButton('✅' if filters['document'] else '❌',
                    callback_data=f'settings#updatefilter-document-{filters["document"]}')
       ],[
       InlineKeyboardButton('🎞️ Videos',
                    callback_data=f'settings_#updatefilter-video-{filters["video"]}'),
       InlineKeyboardButton('✅' if filters['video'] else '❌',
                    callback_data=f'settings#updatefilter-video-{filters["video"]}')
       ],[
       InlineKeyboardButton('📷 Photos',
                    callback_data=f'settings_#updatefilter-photo-{filters["photo"]}'),
       InlineKeyboardButton('✅' if filters['photo'] else '❌',
                    callback_data=f'settings#updatefilter-photo-{filters["photo"]}')
       ],[
       InlineKeyboardButton('🎧 Audios',
                    callback_data=f'settings_#updatefilter-audio-{filters["audio"]}'),
       InlineKeyboardButton('✅' if filters['audio'] else '❌',
                    callback_data=f'settings#updatefilter-audio-{filters["audio"]}')
       ],[
       InlineKeyboardButton('⫷ back',
                    callback_data="settings#main"),
       InlineKeyboardButton('next ⫸',
                    callback_data="settings#nextfilters")
       ]]
  return InlineKeyboardMarkup(buttons) 

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

async def next_filters_buttons(user_id):
  filter = await get_configs(user_id)
  filters = filter['filters']
  buttons = [[
       ],[
       InlineKeyboardButton('🎤 Voices',
                    callback_data=f'settings_#updatefilter-voice-{filters["voice"]}'),
       InlineKeyboardButton('✅' if filters['voice'] else '❌',
                    callback_data=f'settings#updatefilter-voice-{filters["voice"]}')
       ],[
       InlineKeyboardButton('🎭 Animations',
                    callback_data=f'settings_#updatefilter-animation-{filters["animation"]}'),
       InlineKeyboardButton('✅' if filters['animation'] else '❌',
                    callback_data=f'settings#updatefilter-animation-{filters["animation"]}')
       ],[
       InlineKeyboardButton('🃏 Stickers',
                    callback_data=f'settings_#updatefilter-sticker-{filters["sticker"]}'),
       InlineKeyboardButton('✅' if filters['sticker'] else '❌',
                    callback_data=f'settings#updatefilter-sticker-{filters["sticker"]}')
       ],[
       InlineKeyboardButton('▶️ Skip duplicate',
                    callback_data=f'settings_#updatefilter-duplicate-{filter["duplicate"]}'),
       InlineKeyboardButton('✅' if filter['duplicate'] else '❌',
                    callback_data=f'settings#updatefilter-duplicate-{filter["duplicate"]}')
       ],[
       InlineKeyboardButton('📊 Poll',
                    callback_data=f'settings_#updatefilter-poll-{filters["poll"]}'),
       InlineKeyboardButton('✅' if filters['poll'] else '❌',
                    callback_data=f'settings#updatefilter-poll-{filters["poll"]}')
       ],[
       InlineKeyboardButton('🔒 Secure message',
                    callback_data=f'settings_#updatefilter-protect-{filter["protect"]}'),
       InlineKeyboardButton('✅' if filter['protect'] else '❌',
                    callback_data=f'settings#updatefilter-protect-{filter["protect"]}')
       ],[
       InlineKeyboardButton('⫷ back', 
                    callback_data="settings#filters"),
       InlineKeyboardButton('End ⫸',
                    callback_data="settings#main")
       ]]
  return InlineKeyboardMarkup(buttons) 

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
