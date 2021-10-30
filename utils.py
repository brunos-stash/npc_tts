from telegram import Update
import json

with open("conf.json", "r") as f:
    try:
        TELEGRAM_CONFIG = json.load(f)
    except:
        raise Exception("cant read TELEGRAM_CONFIG")
try:
    TELEGRAM_ADMIN_ID = int(TELEGRAM_CONFIG["admin_id"])
except:
    raise Exception("no admin_id in TELEGRAM_CONFIG")

def is_admin(user_id: int) -> bool:
    if user_id != TELEGRAM_ADMIN_ID:
        return False
    else:
        return True
