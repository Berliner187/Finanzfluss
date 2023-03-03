from db_manager import DataBaseManager


USERS_DATA_BASE = 'users.db'
USERS_TABLE_NAME = 'users'

USERS_TABLE = """CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    login TEXT,
    password TEXT
)"""

USERS_TABLE_EXECUTE = f"INSERT INTO {USERS_TABLE_NAME} (login, password) VALUES (?, ?)"

COLUMNS_TABLE_USERS = [
    'id',
    'login',
    'password'
]

# Подключение базы данных
data_base = DataBaseManager()
data_base.create_table(USERS_DATA_BASE, USERS_TABLE)


class Users:
    """
        Класс обработки запросов от пользователя.
        Работа с базой данных пользователей
    """
    @staticmethod
    def save_new_user(data):
        print(data)
        data_base.write_in_table(USERS_DATA_BASE, USERS_TABLE_EXECUTE, data)

    @staticmethod
    def delete_record(criteria):
        data_base.delete_record(USERS_DATA_BASE, criteria)

    # Проверка на вхождение
    @staticmethod
    def select_from_table():
        return data_base.select_from_table(USERS_DATA_BASE, USERS_TABLE_NAME, '*')


class Controller:
    pass
