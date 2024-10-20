import telebot
import requests
import json
import os

# توكن البوت من BotFather
TOKEN = '6755031450:AAHOXhsVHMetq999vNjeyKz5A8ZayAkbiEo'
bot = telebot.TeleBot(TOKEN)

# مسار ملف JSON لحفظ البيانات
DATA_FILE = 'data.json'

# التأكد من أن ملف JSON موجود وإذا لم يكن موجودًا يتم إنشاؤه
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

# دالة لحفظ البيانات في ملف JSON
def save_data(num, access_token, refresh_token):
    with open(DATA_FILE, 'r+') as f:
        data = json.load(f)
        data[num] = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

# دالة لقراءة البيانات من ملف JSON
def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# دالة لتحديث التوكن باستخدام refresh_token
def refresh_access_token(refresh_token):
    token_url = "https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        'Host': 'ibiza.ooredoo.dz',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp/4.9.3',
    }
    payload = {
        "client_id": "ibiza-app",
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        'language': 'AR',
    }
    response = requests.post(token_url, headers=headers, data=payload)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('access_token'), response_data.get('refresh_token')
    return None, None

# دالة لحذف رقم وتوكناته من ملف JSON
def delete_data(num):
    with open(DATA_FILE, 'r+') as f:
        data = json.load(f)
        if num in data:
            del data[num]
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            return True
        return False

# دالة لحذف كل البيانات من ملف JSON
def delete_all_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

# معرفات القنوات والدردشة
CHANNEL_URL_1 = 'https://t.me/Amiimm073'
CHANNEL_ID_1 = '@Amiimm073'
CHANNEL_URL_2 = 'https://t.me/sifonani074'
CHANNEL_ID_2 = '@sifonani074'
GROUP_URL = 'https://t.me/sifonani/your_group_id'
GROUP_ID = '@sifonani'
OWNER_ID = 5863500507

# دالة للتحقق من الاشتراك في القنوات
def check_subscription(user_id):
    try:
        member1 = bot.get_chat_member(CHANNEL_ID_1, user_id)
        member2 = bot.get_chat_member(CHANNEL_ID_2, user_id)
        return member1.status in ['member', 'administrator'] and member2.status in ['member', 'administrator']
    except Exception:
        return False

# دالة بدء المحادثة مع رسالة الترحيب والأزرار
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = "✨ مرحبًا بك في بوتنا الرائع! 🌟 لنبدأ رحلتك. يرجى اختيار أحد الخيارات أدناه:"
    
    markup = telebot.types.InlineKeyboardMarkup()
    start_button = telebot.types.InlineKeyboardButton("🆕 إدخال رقم الهاتف 📞", callback_data="input_phone")
    delete_button = telebot.types.InlineKeyboardButton("🗑️ حذف رقم الهاتف 📞", callback_data="delete_number")
    
    markup.add(start_button)
    markup.add(delete_button)

    # إضافة زر حذف جميع الأرقام للمالك فقط
    if message.from_user.id == OWNER_ID:
        delete_all_button = telebot.types.InlineKeyboardButton("🗑️ حذف جميع الأرقام ❌🔢", callback_data="delete_all_numbers")
        markup.add(delete_all_button)

    if message.from_user.id != OWNER_ID:
        if not check_subscription(message.from_user.id):
            sub_markup = telebot.types.InlineKeyboardMarkup()
            sub_button1 = telebot.types.InlineKeyboardButton("🔔 اشترك في القناة 1", url=CHANNEL_URL_1)
            sub_button2 = telebot.types.InlineKeyboardButton("🔔 اشترك في القناة 2", url=CHANNEL_URL_2)
            sub_button3 = telebot.types.InlineKeyboardButton("👥 انضم للدردشة", url=GROUP_URL)
            sub_markup.add(sub_button1)
            sub_markup.add(sub_button2)
            sub_markup.add(sub_button3)
            bot.send_message(message.chat.id, "🔔 للتمتع بالخدمة، يرجى الاشتراك في القنوات التالية:", reply_markup=sub_markup)
            return

    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

# دالة لمعالجة الأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == "input_phone":
        bot.send_message(call.message.chat.id, "🆕 يرجى إدخال رقم الهاتف (يجب أن يكون رقم يوز):")
    elif call.data == "delete_number":
        bot.send_message(call.message.chat.id, "❌ يرجى إدخال الرقم لحذفه:")
    elif call.data == "delete_all_numbers":
        delete_all_data()
        bot.send_message(call.message.chat.id, "✅ تم حذف جميع الأرقام والتوكنات بنجاح.")

# دالة لمعالجة الرقم المدخل
@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_number(message):
    num = message.text
    data = load_data()
    
    if num in data:
        bot.send_message(message.chat.id, '📶 الرقم موجود بالفعل، يتم الآن محاولة تحديث التوكن...')
        refresh_token = data[num]['refresh_token']
        access_token, new_refresh_token = refresh_access_token(refresh_token)
        
        if access_token:
            bot.send_message(message.chat.id, '✅ تم تحديث التوكن بنجاح! 🚀 يتم الآن إرسال الإنترنت...')
            save_data(num, access_token, new_refresh_token)
            send_internet(message, access_token)
        else:
            bot.send_message(message.chat.id, '❌ فشل في تحديث التوكن، يرجى المحاولة لاحقًا. 🕒')
    else:
        bot.send_message(message.chat.id, '🔍 يتم تحقق من رقمك، إنتظر قليلاً...')
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'ibiza.ooredoo.dz',
            'Connection': 'Keep-Alive',
            'User-Agent': 'okhttp/4.9.3',
        }

        data = {
            'client_id': 'ibiza-app',
            'grant_type': 'password',
            'mobile-number': num,
            'language': 'AR',
        }

        response = requests.post(
            'https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token',
            headers=headers, 
            data=data)
        
        if 'ROOGY' in response.text:
            bot.send_message(message.chat.id, '📥 تم إرسال رمز تحقق SMS، قم بإرساله من فضلك.')
            bot.register_next_step_handler(message, handle_otp, num)
        else:
            bot.send_message(message.chat.id, '❌ فشل في إرسال رمز. 💬')

# دالة لمعالجة الكود المدخل
def handle_otp(message, num):
    otp = message.text
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ibiza.ooredoo.dz',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp',
    }

    data = {
        'client_id': 'ibiza-app',
        'otp': otp,
        'grant_type': 'password',
        'mobile-number': num,
        'language': 'AR',
    }

    response = requests.post(
        'https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token',
        headers=headers,
        data=data
    )
    
    response_data = response.json()
    access_token = response_data.get('access_token')
    refresh_token = response_data.get('refresh_token')

    if access_token and refresh_token:
        bot.send_message(message.chat.id, '✅ التحقق بنجاح! 🎉 الآن، استمتع بالخدمة!')
        save_data(num, access_token, refresh_token)
        send_internet(message, access_token)
    else:
        bot.send_message(message.chat.id, '❌ فشل تحقق من رمز. 💬')

# دالة للتحقق من حجم الإنترنت
def check_internet_volume(access_token):
    url = 'https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/balance'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'language': 'AR',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    accounts = response.json().get('accounts', [])
    
    if len(accounts) > 1:
        return accounts[1].get('value', 'غير متاح')
    else:
        return 'غير متاح'

# دالة لإرسال الإنترنت بشكل متكرر
def send_internet(message, access_token):
    url = 'https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/mgm/info/apply'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'language': 'AR',
        'request-id': 'ef69f4c6-2ead-4b93-95df-106ef37feefd',
        'flavour-type': 'gms',
        'Content-Type': 'application/json'
    }

    mgm_values = ["ABC", "DEF", "GHI", "JKL", "MNO"]

    # التحقق من حجم الإنترنت قبل العملية
    initial_volume = check_internet_volume(access_token)

    max_retries = 10  # عدد المحاولات القصوى لإرسال الإنترنت
    for attempt in range(max_retries):
        for mgm_value in mgm_values:
            payload = {"mgmValue": mgm_value}
            response = requests.post(url, headers=headers, json=payload).text
            
            if 'Request Rejected' in response:
                bot.send_message(message.chat.id, f'❌ فشل في إرسال رمز لـ {mgm_value}')
            else:
                break
        else:
            bot.send_message(message.chat.id, '❌ جميع المحاولات فشلت، يرجى المحاولة لاحقًا.')
            return

    # التحقق من حجم الإنترنت بعد العملية
    final_volume = check_internet_volume(access_token)

    # إرسال الرسالة إلى القناة الثانية
    message_text = (
        f"*YOOZ•SIFO RVS||PROF*\n"
        f"المستخدم: @{message.from_user.username}\n"
        f'🌐 حجم الإنترنت قبل العملية: {initial_volume} GB\n'
        f'🌐 حجم الإنترنت بعد العملية: {final_volume} GB\n'
        f'━━━━━━━━━━━━━━━━━\n'
        f"شكراً لاستخدامكم بوتنا! 🙏\n"
        f"مطور البوت: @SIFO_RVS يشكركم على استعمال خدماتنا! ❤️"
    )
    
    bot.send_message(CHANNEL_ID_2, message_text, parse_mode='Markdown')  # إرسال إلى القناة الثانية

# دالة لحذف رقم وتوكناته
@bot.message_handler(commands=['delete'])
def delete_number(message):
    try:
        num = message.text.split()[1]  # يفترض أن المستخدم يرسل الرقم مع الأمر
        if delete_data(num):
            bot.reply_to(message, f'✅ تم حذف الرقم {num} بنجاح.')
        else:
            bot.reply_to(message, f'❌ الرقم {num} غير موجود.')
    except IndexError:
        bot.reply_to(message, '⚠️ يرجى إدخال الرقم بعد الأمر. مثال: /delete 1234567890')

# دالة لحذف جميع البيانات
@bot.message_handler(commands=['delete_all'])
def delete_all(message):
    delete_all_data()
    bot.reply_to(message, '✅ تم حذف جميع الأرقام والتوكنات بنجاح.')

# بدء البوت
bot.polling()