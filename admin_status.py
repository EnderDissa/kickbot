import json

class AdminStatusManager:
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

    # Формируем ключ на основе двух user_id (например, "123-456" или "456-123")
    def create_key(self, user_id_1, user_id_2):
        # Приводим оба user_id к строке, чтобы избежать ошибки сравнения
        user_id_1 = str(user_id_1)
        user_id_2 = str(user_id_2)
        return f"{min(user_id_1, user_id_2)}-{max(user_id_1, user_id_2)}"

    # Добавляем пару пользователей и их статус
    def add_user_pair(self, user_id_1, user_id_2, status):
        key = self.create_key(user_id_1, user_id_2)
        self.data[key] = status
        self.save_data()

    # Проверка, находится ли пара пользователей в одной записи и какой у них статус
    def get_user_pair_status(self, user_id_1, user_id_2):
        key = self.create_key(user_id_1, user_id_2)
        return self.data.get(key, "Статус не найден")
