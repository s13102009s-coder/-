import time

pending_messages = {}

def add_pending(placeholder_msg_id, original_text, original_sender_id, chat_id):
    pending_messages[placeholder_msg_id] = {
        "original_text": original_text,
        "original_sender_id": original_sender_id,
        "chat_id": chat_id,
        "timestamp": time.time(),
        "locked": False
    }

def get_pending(placeholder_msg_id):
    return pending_messages.get(placeholder_msg_id)

def remove_pending(placeholder_msg_id):
    if placeholder_msg_id in pending_messages:
        del pending_messages[placeholder_msg_id]

def set_locked(placeholder_msg_id):
    if placeholder_msg_id in pending_messages:
        pending_messages[placeholder_msg_id]["locked"] = True