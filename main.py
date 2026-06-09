import requests
import httpx
import asyncio
import random
import string
import uuid
import re
import ssl
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging
from user_agent import generate_user_agent
from flask import Flask
from threading import Thread

app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7802803805:AAHpQsYUtbOth1X1jgpJXcNn5yp0pWblgpo"

ADMIN_IDS = {1492627428}
authorized_users = set()

user_states = {}
user_data = {}
user_passwords = {}
user_modes = {}

PROXY_LIST = [
    "http://e406afdd9a5feaaebb99:93fb5b64e197f5b9@gw.dataimpulse.com:823",
]

COOKIES = {
    "csrftoken": "qXbOywPKhDdMfdTceKhs2DcocVgMz4q8",
    "mid": "adiAuAAEAAFqNhj2f7KBf56OjV5_",
    "ig_did": "6C2A174F-093F-4BAC-8DDF-B7D6527F73AE",
}

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=1.0",
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "x-ig-app-id": "936619743392459",
    "x-csrftoken": "qXbOywPKhDdMfdTceKhs2DcocVgMz4q8",
    "x-requested-with": "XMLHttpRequest",
}

JAZOEST_LIST = ["22603", "22913", "22785", "22841", "22567"]

def get_safe_context():
    context = ssl.create_default_context()
    context.set_ciphers('DEFAULT@SECLEVEL=1')
    return context

rate_limit_state = {
    "failures": 0,
    "base_delay": 0.5,
    "last_request_time": 0
}

def is_authorized(user_id):
    return user_id in ADMIN_IDS or user_id in authorized_users

def generate_random_password():
    length = 12
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_device_info():
    ANDROID_ID = f"android-{''.join(random.choices(string.hexdigits.lower(), k=16))}"
    USER_AGENT = f"Instagram 394.0.0.46.81 Android ({random.choice(['28/9','29/10','30/11','31/12'])}; {random.choice(['240dpi','320dpi','480dpi'])}; {random.choice(['720x1280','1080x1920','1440x2560'])}; {random.choice(['samsung','xiaomi','huawei','oneplus','google'])}; {random.choice(['SM-G975F','Mi-9T','P30-Pro','ONEPLUS-A6003','Pixel-4'])}; intel; en_US; {random.randint(100000000,999999999)})"
    WATERFALL_ID = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp())
    return ANDROID_ID, USER_AGENT, WATERFALL_ID, timestamp

def make_headers(mid="", user_agent=""):
    return {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Bloks-Version-Id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
        "X-Mid": mid,
        "User-Agent": user_agent,
        "Content-Length": "9481"
    }

def get_username_from_id(user_id):
    try:
        url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"
        headers = {"User-Agent": "Instagram 219.0.0.12.117 Android"}
        r = requests.get(url, headers=headers, timeout=10)
        return r.json()["user"]["username"]
    except:
        return "Unknown"

def reset_password_sync(reset_link, custom_password):
    try:
        ANDROID_ID, USER_AGENT, WATERFALL_ID, timestamp = generate_device_info()
        
        uidb36 = reset_link.split("uidb36=")[1].split("&token=")[0]
        token = reset_link.split("&token=")[1].split(":")[0]
        
        PASSWORD = f'#PWD_INSTAGRAM:0:{timestamp}:{custom_password}'
        
        url = "https://i.instagram.com/api/v1/accounts/password_reset/"
        data = {
            "source": "one_click_login_email",
            "uidb36": uidb36,
            "device_id": ANDROID_ID,
            "token": token,
            "waterfall_id": WATERFALL_ID
        }
        r = requests.post(url, headers=make_headers(user_agent=USER_AGENT), data=data, timeout=15)
        
        if "user_id" not in r.text:
            return {"success": False, "error": f"Reset request failed: {r.text[:100]}"}
        
        mid = r.headers.get("Ig-Set-X-Mid")
        resp_json = r.json()
        user_id = resp_json.get("user_id")
        cni = resp_json.get("cni")
        nonce_code = resp_json.get("nonce_code")
        challenge_context = resp_json.get("challenge_context")
        
        url2 = "https://i.instagram.com/api/v1/bloks/apps/com.instagram.challenge.navigation.take_challenge/"
        data2 = {
            "user_id": str(user_id),
            "cni": str(cni),
            "nonce_code": str(nonce_code),
            "bk_client_context": '{"bloks_version":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","styles_id":"instagram"}',
            "challenge_context": str(challenge_context),
            "bloks_versioning_id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
            "get_challenge": "true"
        }
        r2 = requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data2, timeout=15).text
        
        challenge_context_final = r2.replace('\\', '').split(f'(bk.action.i64.Const, {cni}), "')[1].split('", (bk.action.bool.Const, false)))')[0]
        
        data3 = {
            "is_caa": "False",
            "source": "",
            "uidb36": "",
            "error_state": {"type_name":"str","index":0,"state_id":1048583541},
            "afv": "",
            "cni": str(cni),
            "token": "",
            "has_follow_up_screens": "0",
            "bk_client_context": {"bloks_version":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","styles_id":"instagram"},
            "challenge_context": challenge_context_final,
            "bloks_versioning_id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
            "enc_new_password1": PASSWORD,
            "enc_new_password2": PASSWORD
        }
        requests.post(url2, headers=make_headers(mid, USER_AGENT), json=data3, timeout=15)
        
        username = get_username_from_id(user_id)
        return {"success": True, "username": username, "password": custom_password, "user_id": user_id}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def reset_password_from_link(reset_link, custom_password):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, reset_password_sync, reset_link, custom_password)

async def send_reset_email(user: str, proxy: str = None) -> str:
    global rate_limit_state
    
    now = asyncio.get_event_loop().time()
    elapsed = now - rate_limit_state["last_request_time"]
    if elapsed < rate_limit_state["base_delay"]:
        await asyncio.sleep(rate_limit_state["base_delay"] - elapsed)
    
    for attempt in range(1, 4):
        try:
            if proxy is None and PROXY_LIST:
                proxy = random.choice(PROXY_LIST)
            
            async with httpx.AsyncClient(
                http2=True,
                verify=get_safe_context(),
                timeout=20,
                proxy=proxy if proxy else None
            ) as client:
                response = await client.post(
                    "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/?hl=en",
                    headers=HEADERS,
                    cookies=COOKIES,
                    data={
                        "email_or_username": user,
                        "jazoest": random.choice(JAZOEST_LIST)
                    }
                )
                
                rate_limit_state["last_request_time"] = asyncio.get_event_loop().time()
                
                if response.status_code == 429:
                    rate_limit_state["failures"] += 1
                    rate_limit_state["base_delay"] = min(rate_limit_state["base_delay"] * 2, 10)
                    wait = 5 * attempt
                    await asyncio.sleep(wait)
                    continue
                
                if response.status_code != 200:
                    if attempt < 3:
                        await asyncio.sleep(2)
                        continue
                    return f"❌ {user} - HTTP {response.status_code}"
                
                if rate_limit_state["failures"] > 0:
                    rate_limit_state["failures"] -= 1
                if rate_limit_state["base_delay"] > 0.5:
                    rate_limit_state["base_delay"] = max(0.5, rate_limit_state["base_delay"] // 1.5)
                
                try:
                    result = response.json()
                    contact = result.get('contact_point', '')
                    if contact and '***' in contact:
                        return f"✅ {user} - {contact}"
                    elif contact:
                        return f"✅ {user} - Sent"
                    else:
                        error_text = str(result).lower()
                        if 'no_user' in error_text or 'user not found' in error_text:
                            return f"❌ {user} - Not found"
                        return f"✅ {user} - Sent"
                except:
                    return f"✅ {user} - Sent"
                    
        except Exception as e:
            if attempt < 3:
                await asyncio.sleep(2)
                continue
            return f"❌ {user} - {str(e)[:50]}"
    
    return f"❌ {user} - Failed"

async def background_bulk_reset(chat_id, message_id, context, usernames):
    total = len(usernames)
    sem = asyncio.Semaphore(3)
    
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"⏳ Processing {total} users concurrently with proxies..."
    )
    
    async def process_one(username, index):
        async with sem:
            await asyncio.sleep(random.uniform(0.2, 0.8))
            result = await send_reset_email(username)
            return f"{index}. {result}"
    
    tasks = [process_one(u, i+1) for i, u in enumerate(usernames)]
    results = await asyncio.gather(*tasks)
    
    for j in range(0, len(results), 10):
        chunk = "\n\n".join(results[j:j+10])
        if j == 0:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=chunk)
        else:
            await context.bot.send_message(chat_id=chat_id, text=chunk)
        await asyncio.sleep(0.5)

async def background_single_reset(chat_id, message_id, context, username):
    result = await send_reset_email(username)
    await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result)

async def background_link_reset(chat_id, message_id, context, reset_link, password):
    result = await reset_password_from_link(reset_link, password)
    if result.get("success"):
        response = f"✅ @{result['username']}\n🔑 `{result['password']}`\n🆔 `{result['user_id']}`"
    else:
        response = f"❌ {result.get('error', 'Failed')}"
    await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=response, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    user_id = update.effective_user.id
    user_states.pop(user_id, None)
    user_data.pop(user_id, None)
    user_modes.pop(user_id, None)
    keyboard = [
        [InlineKeyboardButton("🤖 Auto", callback_data='mode_auto'),
         InlineKeyboardButton("👤 Manual", callback_data='mode_manual')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✨ *Instagram Reset Bot*\n\nSelect mode:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def setpassword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        return
    if not context.args or len(context.args[0]) < 6:
        await update.message.reply_text("Usage: /setpassword <6+ chars>")
        return
    user_passwords[user_id] = context.args[0]
    await update.message.reply_text(f"✅ `{context.args[0]}`", parse_mode='Markdown')

async def revokepassword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        return
    if user_id in user_passwords:
        del user_passwords[user_id]
        await update.message.reply_text("✅ Removed")
    else:
        await update.message.reply_text("No password set")

async def accessgrant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("/accessgrant <id>")
        return
    try:
        user_id = int(context.args[0])
        authorized_users.add(user_id)
        await update.message.reply_text(f"✅ Granted: {user_id}")
    except:
        await update.message.reply_text("Invalid ID")

async def accessrevoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("/accessrevoke <id>")
        return
    try:
        user_id = int(context.args[0])
        authorized_users.discard(user_id)
        await update.message.reply_text(f"✅ Revoked: {user_id}")
    except:
        await update.message.reply_text("Invalid ID")

async def accesslist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not authorized_users:
        await update.message.reply_text("No users")
        return
    users = "\n".join([f"• `{uid}`" for uid in sorted(authorized_users)])
    await update.message.reply_text(users, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not is_authorized(user_id):
        await query.edit_message_text("❌ Unauthorized")
        return
    if query.data == 'mode_auto':
        user_modes[user_id] = 'auto'
        user_states[user_id] = 'ready'
        await query.edit_message_text(
            "🤖 *Auto Mode*\n\nSend username, bulk list, or reset link",
            parse_mode='Markdown'
        )
    elif query.data == 'mode_manual':
        user_modes[user_id] = 'manual'
        keyboard = [
            [InlineKeyboardButton("📧 Single", callback_data='single_reset')],
            [InlineKeyboardButton("📊 Bulk", callback_data='bulk_reset')],
            [InlineKeyboardButton("🔑 Link", callback_data='link_to_pass')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("👤 *Manual Mode*", reply_markup=reply_markup, parse_mode='Markdown')
    elif query.data == 'single_reset':
        user_states[user_id] = 'waiting_single'
        await query.edit_message_text("Send username/email:")
    elif query.data == 'bulk_reset':
        user_states[user_id] = 'waiting_bulk'
        await query.edit_message_text("Send list (max 30, one per line):")
    elif query.data == 'link_to_pass':
        user_states[user_id] = 'waiting_link'
        await query.edit_message_text("Send reset link:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized")
        return
    mode = user_modes.get(user_id, 'auto')

    if mode == 'auto':
        if "uidb36=" in text and "token=" in text:
            msg = await update.message.reply_text("⏳ Processing reset link in background...")
            password = user_passwords.get(user_id, generate_random_password())
            asyncio.create_task(background_link_reset(msg.chat_id, msg.message_id, context, text, password))
            return
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) > 1:
            if len(lines) > 50:
                await update.message.reply_text("Max 50")
                return
            msg = await update.message.reply_text(f"⏳ Processing {len(lines)} users in background...")
            asyncio.create_task(background_bulk_reset(msg.chat_id, msg.message_id, context, lines))
            return
        
        msg = await update.message.reply_text("⏳ Sending reset email in background...")
        asyncio.create_task(background_single_reset(msg.chat_id, msg.message_id, context, text))
        return

    elif mode == 'manual':
        state = user_states.get(user_id)
        if not state:
            await update.message.reply_text("Use /start")
            return
        
        if state == 'waiting_single':
            msg = await update.message.reply_text("⏳ Processing in background...")
            asyncio.create_task(background_single_reset(msg.chat_id, msg.message_id, context, text))
            del user_states[user_id]
        
        elif state == 'waiting_bulk':
            usernames = [line.strip() for line in text.split('\n') if line.strip()]
            if len(usernames) > 30:
                await update.message.reply_text("Max 30")
                return
            if not usernames:
                await update.message.reply_text("Send at least one")
                return
            msg = await update.message.reply_text(f"⏳ Processing {len(usernames)} users in background...")
            asyncio.create_task(background_bulk_reset(msg.chat_id, msg.message_id, context, usernames))
            del user_states[user_id]
        
        elif state == 'waiting_link':
            user_data[user_id] = {'reset_link': text}
            user_states[user_id] = 'waiting_password'
            await update.message.reply_text("Send new password (6+ chars):")
        
        elif state == 'waiting_password':
            if len(text) < 6:
                await update.message.reply_text("Min 6 characters")
                return
            reset_link = user_data.get(user_id, {}).get('reset_link', '')
            msg = await update.message.reply_text("⏳ Resetting password in background...")
            asyncio.create_task(background_link_reset(msg.chat_id, msg.message_id, context, reset_link, text))
            user_data.pop(user_id, None)
            user_states.pop(user_id, None)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

def main():
    keep_alive()
    print("🤖 Bot starting WITH PROXY ROTATION (high speed, no 429) + Flask keep-alive...")
    if PROXY_LIST:
        print(f"✅ Loaded {len(PROXY_LIST)} proxy(ies). Will rotate automatically.")
    else:
        print("⚠️ No proxies configured. Will use direct connection (risk of 429).")
    app = (Application.builder()
           .token(BOT_TOKEN)
           .concurrent_updates(True)
           .connection_pool_size(8)
           .build())
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setpassword", setpassword))
    app.add_handler(CommandHandler("revokepassword", revokepassword))
    app.add_handler(CommandHandler("accessgrant", accessgrant))
    app.add_handler(CommandHandler("accessrevoke", accessrevoke))
    app.add_handler(CommandHandler("accesslist", accesslist))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
