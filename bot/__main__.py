from datetime import datetime

import pyrogram

from admin_status import AdminStatusManager
from chats_DB import ChatUserDatabase
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from pyrogram.errors import ChatAdminRequired, ChatWriteForbidden, UsernameNotOccupied, UserNotParticipant, \
    MessageTooLong
from pyrogram.types import BotCommand, ChatMember
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
api_id = ''
api_hash = ''
bot_token=''
app = Client("my_account", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
user_status_manager = AdminStatusManager('admin_statuses.json')
chat_db=ChatUserDatabase('chat_user_database.json')

def message_sender(tts,message):
    if tts!='':
        try:
            message.reply_text(tts)
        except MessageTooLong:
            ttses=[]
            for t in range((len(tts)//4096+1)):
                ttses.append(tts[t*4096:(t+1)*4096])
            for t in ttses:
                message.reply_text(t)

def check_suspicious(channel):
    tts=''
    suspicious=[]
    users=check_user_photos(channel)
    for user_id,user_date in users.items():

        if user_date != 0:
            if (1720150200 <= user_date <= 1720157400):
                suspicious.append(user_id)
        else:
            photo_date='аватарок нет'
    return suspicious
def check_unsuspicious(channel):
    tts=''
    unsuspicious=[]
    users=check_user_photos(channel)
    for user_id,user_date in users.items():

        if user_date != 0:
            if (user_date<=1720150200 or user_date>=1720157400):
                unsuspicious.append(user_id)
        else:
            photo_date='аватарок нет'
    return unsuspicious

def check_user_photos(channel):
    names=[]
    name_photo=dict()
    users=chat_db.get_all_users(channel)

    for user_id, user_info in users.items():
        name_photo.update({user_id: user_info['photo_date']})
    return name_photo

    # for member in chat_db.get_all_users(channel):
    #
    #     user = member.user
    #     user_meta = chat_db.get_user_info(channel, user.id)
    #     if user_meta['photo_date'] != 0:
    #         photo_date = str(datetime.utcfromtimestamp(int(user_meta['photo_date'])).strftime('%Y-%m-%d %H:%M:%S'))
    #     else:
    #         photo_date = 'аватарок нет'
    #     tts += user_meta['first_name'] + '—' + photo_date + '\n'
    # return tts


    # for user_id, user_info in users.items():
    #
    #     #tts+= f"User ID: {user_id}"
    #     #tts+=f"First Name: {user_info['first_name']}")
    #     #print(f"Photo Dates: {user_info['photo_dates']}")
    #     # Выполните дополнительные действия с user_info при необходимости
    #     tts+=f"\n"

def get_name_by_id(id,channel):
    info=chat_db.get_user_info(channel, id)
    return info['first_name']
def get_date_by_id(id,channel):
    info=chat_db.get_user_info(channel, id)
    return datetime.utcfromtimestamp(int(info['photo_date'])).strftime('%d-%m-%Y %H:%M:%S')

def get_admin_status(id,channel):
    status=user_status_manager.get_user_pair_status(id, channel)
    return status

def kick_user(id,channel):
    app.ban_chat_member(channel, id)
    return True

# Обработчик команды /start
@app.on_message(filters.command("start"))
def start(client, message):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Добавить в группу", url="http://t.me/dormentorkickbot?startgroup=test")]]
    )
    message.reply_text("Привет! Я бот дорментора.", reply_markup=keyboard)


@app.on_message(filters.command("admin"))
def admin(client, message):
    tts=''
    msg=message.text.split()
    channel=msg[1]
    try:
        chat_bot = app.get_chat_member(channel, "me")
        if chat_bot.status == ChatMemberStatus.ADMINISTRATOR:
            flag_botadmin=1
        else:
            tts+="бот не является администратором в канале.\n"

        user_id=message.from_user.id
        chat_member=app.get_chat_member(channel, user_id)
        if (chat_member.status == ChatMemberStatus.OWNER or chat_member.status == ChatMemberStatus.ADMINISTRATOR):
            flag_useradmin=1
        else:
            tts+='вы не являетесь администратором канала!\n'

        if (flag_useradmin and flag_botadmin):
            user_status_manager.add_user_pair(user_id, channel, "1")
            tts='УСПЕХ'



    except ChatAdminRequired:
        message.reply_text("У бота нет прав администратора для выполнения этого действия!")
    except UserNotParticipant:
        message.reply_text("Бот не может писать в канал. Возможно, его нет в канале.")
    except ValueError:
        message.reply_text("айдишник принадлежит не каналу!")
    except UsernameNotOccupied:
        message.reply_text("айдишник никому не принадлежит!")
    message_sender(tts, message)

@app.on_message(filters.command("get_photos"))
def get_photos(client, message):
    tts=''
    id=message.from_user.id
    channel = message.text.split()[1]
    status=get_admin_status(id,channel)
    if status=='1':
        user_info=check_user_photos(channel)
        if len(user_info)==0:
            tts='информации нет. попробуйте /check'
        for user_name, user_date in user_info.items():
            tts+=get_name_by_id(user_name,channel) +' — '
            if user_date != 0:
                tts += f"{datetime.utcfromtimestamp(int(user_date)).strftime('%d-%m-%Y %H:%M:%S')}"
            else:
                tts += f"аватарок нет"
            tts+='\n'
                # app.ban_chat_member(channel, user_id_to_kick)  # Раскомментируйте, если нужно
        tts+='всего: '+ str(len(user_info))
    else:
        tts='в вашем сообщении ошибка:\n айди не существует или вы не являетесь его администратором'
    message_sender(tts, message)

@app.on_message(filters.command("check"))
def check(client, message):
    msg = message.text.split()
    channel = msg[1]
    user_status = user_status_manager.get_user_pair_status(message.from_user.id, channel)
    if user_status == '1':
        print(f"User ID: {message.from_user.id}, чекает: @{channel}")
        tts = ''
        i = 0
        added_users = 0
        updated_users = 0
        current_user_ids = set()

        # Получаем список пользователей, сохраненных в базе данных до обновления
        stored_users = chat_db.get_all_users(channel)
        stored_user_ids = set(stored_users.keys())

        # Получаем текущих участников канала
        for member in app.get_chat_members(channel):
            user = member.user
            i += 1
            user_id_str = str(user.id)
            current_user_ids.add(user_id_str)  # Собираем ID текущих пользователей

            photo_dates = []
            photo_date_total = 0
            k = 0

            # Получаем фотографии профиля пользователя
            for photo in app.get_chat_photos(user.id):
                photo_dates.append(photo.date.strftime('%Y-%m-%d %H:%M:%S'))
                photo_date_total += photo.date.timestamp()
                k += 1

            photo_date_mid = int(photo_date_total // k) if k > 0 else 0

            user_info = {
                "user_id": user.id,
                "first_name": user.first_name or "Имя не указано",
                "username": user.username or "Username не указан",
                "photo_dates": photo_dates,
                "photo_date": photo_date_mid
            }

            # Проверяем, есть ли пользователь в базе данных
            if user_id_str not in stored_user_ids:
                # Новый пользователь
                added_users += 1
                chat_db.add_user_info(channel, user.id, user_info)
            else:
                # Пользователь уже есть в базе данных, проверяем обновления
                stored_user_info = stored_users[user_id_str]
                if stored_user_info.get('photo_date') != photo_date_mid:
                    # Обновилась аватарка пользователя
                    updated_users += 1
                    # Обновляем информацию в базе данных
                    chat_db.add_user_info(channel, user.id, user_info)
                else:
                    # Данные не изменились, ничего не делаем
                    pass

        # Определяем пользователей, которые вышли из канала
        users_to_remove = stored_user_ids - current_user_ids

        # Удаляем пользователей, которые больше не в канале
        for user_id in users_to_remove:
            chat_db.remove_user(channel, user_id)

        tts = (f"Обработано пользователей: {i}.\n"
               f"Добавлено пользователей: {added_users}\n"
               f"Обновлено пользователей: {updated_users}\n"
               f"Удалено пользователей: {len(users_to_remove)}")
        print(tts)

        message_sender(tts, message)
    else:
        print(f"User ID: {message.from_user.id}, пытался прочекать: @{channel}")


@app.on_message(filters.command("get_suspicious"))
def get_suspicious(client, message):
    tts=''
    msg = message.text.split()
    channel = msg[1]
    user_status = user_status_manager.get_user_pair_status(message.from_user.id, channel)
    if (user_status == '1'):
        print(f"User ID: {message.from_user.id}, проверяет на подозрительность: @{channel}")
        suspicious=check_suspicious(channel)
        for _ in suspicious:
            tts+=get_name_by_id(_,channel)+' — '+get_date_by_id(_,channel)+'\n'
        tts+="\nвсего: "+str(len(suspicious))
    else:
        print(f"User ID: {message.from_user.id}, пытался проверить на подозрительность: @{channel}")
    message_sender(tts, message)
@app.on_message(filters.command("get_unsuspicious"))
def get_unsuspicious(client, message):
    tts=''
    msg = message.text.split()
    channel = msg[1]
    user_status = user_status_manager.get_user_pair_status(message.from_user.id, channel)
    if (user_status == '1'):
        print(f"User ID: {message.from_user.id}, проверяет на подозрительность: @{channel}")
        unsuspicious=check_unsuspicious(channel)
        for _ in unsuspicious:
            tts+=get_name_by_id(_,channel)+' — '+get_date_by_id(_,channel)+'\n'
        tts+="\nвсего: "+str(len(unsuspicious))
    else:
        print(f"User ID: {message.from_user.id}, пытался проверить на подозрительность: @{channel}")
    message_sender(tts, message)

@app.on_message(filters.command("kick_suspicious"))
def kick_suspicious(client, message):
    tts=''
    msg = message.text.split()
    channel = msg[1]
    user_status = user_status_manager.get_user_pair_status(message.from_user.id, channel)
    if (user_status == '1'):
        print(f"User ID: {message.from_user.id}, проверяет на подозрительность: @{channel}")
        k=0
        suspicious=check_suspicious(channel)
        for bot in suspicious:
            k+=1
            kick_user(bot,channel)
            tts+=get_name_by_id(bot,channel)+'\n'
            if k>1: break#test
        tts+='всего кикнуто: ' +str(k)
    else:
        print(f"User ID: {message.from_user.id}, пытался кикнуть подозрительных: @{channel}")
    message_sender(tts, message)


async def set_commands(client):
    await client.set_bot_commands([
        BotCommand("start", "Запустить бота"),
        BotCommand("get_photos", "Получить фотографии пользователей"),
        # Добавьте другие команды при необходимости
    ])

# Основная функция для запуска бота и установки команд
async def main():

    await app.start()

    await set_commands(app)

    await app.idle()  # Держит бота запущенным

# Запуск бота
print("Бот запущен и команды установлены.")
app.run()