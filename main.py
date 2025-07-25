# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio, logging
from config import Config
from pyrogram import Client as VJ, idle
from typing import Union, Optional, AsyncGenerator
from logging.handlers import RotatingFileHandler
from plugins.regix import restart_forwards

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('bot.log', maxBytes=5242880, backupCount=5),  # 5MB per file, keep 5 files
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

if __name__ == "__main__":
    try:
        VJBot = VJ(
            "VJ-Forward-Bot",
            bot_token=Config.BOT_TOKEN,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            sleep_threshold=120,
            plugins=dict(root="plugins")
        )
        
        async def iter_messages(
            self,
            chat_id: Union[int, str],
            limit: int,
            offset: int = 0,
        ) -> Optional[AsyncGenerator["types.Message", None]]:
            """Iterate through a chat sequentially.
            This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
            you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
            single call.
            Parameters:
                chat_id (``int`` | ``str``):
                    Unique identifier (int) or username (str) of the target chat.
                    For your personal cloud (Saved Messages) you can simply use "me" or "self".
                    For a contact that exists in your Telegram address book you can use his phone number (str).
                    
                limit (``int``):
                    Identifier of the last message to be returned.
                    
                offset (``int``, *optional*):
                    Identifier of the first message to be returned.
                    Defaults to 0.
            Returns:
                ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
            Example:
                .. code-block:: python
                    for message in app.iter_messages("pyrogram", 1, 15000):
                        print(message.text)
            """
            current = offset
            while True:
                try:
                    new_diff = min(200, limit - current)
                    if new_diff <= 0:
                        return
                    messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
                    for message in messages:
                        yield message
                        current += 1
                except Exception as e:
                    logger.error(f"Error in iter_messages: {e}", exc_info=True)
                    break
               
        async def main():
            try:
                await VJBot.start()
                bot_info = await VJBot.get_me()
                logger.info(f"Bot started as @{bot_info.username}")
                await restart_forwards(VJBot)
                logger.info("Bot is ready to use")
                await idle()
            except Exception as e:
                logger.error(f"Error in main: {e}", exc_info=True)
                raise

        logger.info("Starting bot...")
        asyncio.get_event_loop().run_until_complete(main())
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}", exc_info=True)
        raise

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
