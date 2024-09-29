import json

class ChatUserDatabase:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

    # Загрузка данных из файла
    def load_data(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    # Сохранение данных в файл
    def save_data(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    # Добавляем информацию о пользователе в чат
    def add_user_info(self, chat_id, user_id, user_info):
        chat_id = str(chat_id)
        user_id = str(user_id)

        if chat_id not in self.data:
            self.data[chat_id] = {}  # Создаем новый чат, если его нет

        # Добавляем или обновляем информацию о пользователе
        self.data[chat_id][user_id] = user_info
        self.save_data()

    # Получаем информацию о пользователе в конкретном чате
    def get_user_info(self, chat_id, user_id):
        chat_id = str(chat_id)
        user_id = str(user_id)

        if chat_id in self.data and user_id in self.data[chat_id]:
            return self.data[chat_id][user_id]
        else:
            return "Информация не найдена"

    # Получаем всех пользователей в конкретном чате
    def get_all_users(self, chat_id):
        chat_id = str(chat_id)
        users = self.data.get(chat_id, {})
        if isinstance(users, dict):
            return users  # Возвращает словарь {user_id: user_info, ...}
        else:
            # Логируем предупреждение о неверной структуре данных
            print(f"Warning: Expected dict for chat_id {chat_id}, but got {type(users)}")
            return {}

    # Удаление пользователя из чата
    def remove_user(self, chat_id, user_id):
        chat_id = str(chat_id)
        user_id = str(user_id)

        if chat_id in self.data and user_id in self.data[chat_id]:
            del self.data[chat_id][user_id]
            self.save_data()
            return f"Пользователь {user_id} удален из чата {chat_id}"
        else:
            return "Пользователь не найден"
