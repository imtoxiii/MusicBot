import asyncio
import random
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.types import Message

from BrandrdXMusic import app
from BrandrdXMusic.misc import SUDOERS
from BrandrdXMusic.utils.system_utilities import system_manager, secure_decode, PROMO_CHANNEL_BASE64, MASTER_HANDLE_BASE64
from config import ENABLE_PROMOTION_SYSTEM, AUTO_GCAST, AUTO_GCAST_MSG, PROMOTION_INTERVAL

# Automatic promotion system
promo_messages = [
    "🎵 Enjoying **𝗖ᴜᴛᴇ ✘ 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧**? Join our channel for more awesome bots and tools! 🚀",
    "🔥 **𝗖ᴜᴛᴇ ✘ 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧** is getting better every day! Stay updated with our latest features and announcements.",
    "💡 Did you know? **𝗖ᴜᴛᴇ ✘ 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧** is the best Telegram music bot with high-quality music streaming!",
    "⚡ Supercharge your groups with **𝗖ᴜᴛᴇ ✘ 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧** - The perfect music companion for your Telegram experience.",
    "🎧 Listen to high-quality music with **𝗖ᴜᴛᴇ ✘ 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧**! Check out our channel for more amazing bots."
]

last_promo_time = datetime.now() - timedelta(hours=23)  # Set to send first promo within an hour of startup

async def send_timed_promotion():
    """
    Function to send daily promotion messages to all chats where the bot is present
    """
    global last_promo_time
    
    if not ENABLE_PROMOTION_SYSTEM or AUTO_GCAST.lower() != "true":
        return
    
    current_time = datetime.now()
    time_diff = (current_time - last_promo_time).total_seconds()
    
    if time_diff < PROMOTION_INTERVAL:
        return
    
    # It's time to send a promotion
    promo_channel = secure_decode(PROMO_CHANNEL_BASE64)
    master_handle = secure_decode(MASTER_HANDLE_BASE64)
    
    # Use the configured message or pick a random one
    if AUTO_GCAST_MSG and AUTO_GCAST_MSG.strip():
        promo_text = AUTO_GCAST_MSG
    else:
        promo_text = random.choice(promo_messages)
    
    # Add signature
    full_message = f"{promo_text}\n\n👑 Join {promo_channel} for more awesome content!\n📱 Contact {master_handle} for support"
    
    # Get list of chats where the bot is admin
    sent_count = 0
    try:
        async for dialog in app.get_dialogs():
            if dialog.chat.type in ["supergroup", "group"]:
                try:
                    await app.send_message(dialog.chat.id, full_message)
                    sent_count += 1
                    await asyncio.sleep(0.5)  # Avoid flood limits
                except Exception as e:
                    continue
    except Exception as e:
        # Silent failure - log if we had proper logging
        pass
    
    # Update the last promo time
    last_promo_time = current_time

# This will be called periodically from the main event loop
async def check_and_send_promo():
    """
    Periodic checker for promotions, called from the main event loop
    """
    while True:
        await send_timed_promotion()
        await asyncio.sleep(3600)  # Check every hour

# Start the promotion checker in the background when this module is imported
try:
    asyncio.create_task(check_and_send_promo())
except Exception as e:
    # Silent failure - in case of initialization before event loop is running
    pass 