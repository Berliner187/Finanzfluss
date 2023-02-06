# -*- coding: UTF-8 -*-
"""
    Finanzfluss - Finance Flow App
    Приложение позволяет управлять денежными потоками, рассчитывать доход от активов,
    а также анализировать транзакции
    Copyright (C) 2023 by Berliner187

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
"""
from datetime import datetime
import sqlite3


class Transaction:
    def __init__(self, category, amount, debit_account, replenishment_account, description):
        self.category = category
        self.amount = amount   # Сумма
        self.debit_account = debit_account  # Откуда
        self.replenishment_account = replenishment_account  # Куда
        self.description = description  # Описание
        # self.time_transaction = datetime.now()

    # def write_transaction(self):


class DataBaseManager:
    """
        Класс для работы с базой данных.
        Конструктор
    """
    @staticmethod
    def connect_db(data_base):
        return sqlite3.connect(data_base)

    def get_cursor_db(self, data_base):
        return self.connect_db(data_base).cursor()

    # Создание таблицы
    def create_table(self, date_base, table):
        """
            id - Уникальный id облигации, меняется автоматически
            TICKER - Тикер облигации
            BOND - Название облигации
            NOMINAL - Номинал облигации
            AVERAGE PRICE - Стоимость на момент покупки (средняя в портфеле)
            QUANTITY - Количество бумаг в портфеле
            COUPON VALUE - Величина портфеля
            ACI - НКД - Добавляется на момент покупки
            number_of_payments_per_year - Кол-во выплат в год
            total_payments - Всего выплат
            date_of_purchase - Дата покупки
        """
        cursor_data_base = self.get_cursor_db(date_base)
        cursor_data_base.execute(table)

    # Запись в таблицу
    def write_in_table(self, data_base, table, data):
        db = self.connect_db(data_base)
        cursor = db.cursor()
        print('База данных - Запись - ', data)
        print('База данных - Запись (длина) - ', len(data))
        cursor.execute(table, data)
        db.commit()
        db.close()

    # Удаление записи из таблицы по ID
    def delete_record(self, data_base, criteria):
        db = self.connect_db(data_base)
        cursor = db.cursor()
        cursor.execute(f"DELETE from bonds WHERE id = ?", (criteria, ))
        db.commit()
        db.close()

    # Выборка строки по условию
    def select_row_from_table(self, data_base, data_base_table, where, what, condition):
        cursor = self.get_cursor_db(data_base)
        cursor.execute(f"""SELECT {where} FROM {data_base_table} WHERE "{what}" = '{condition}'""")
        return cursor.fetchone()

    # Выборка данных по условию
    def select_from_table(self, data_base, table_name, what):
        cursor = self.get_cursor_db(data_base)
        cursor.execute(f"SELECT {what} FROM {table_name}")
        return cursor.fetchall()

    # Поиск конкретной бумаги
    def bond_row(self, data_base, what, criteria):
        cursor = self.get_cursor_db(self.connect_db(data_base))
        return cursor.execute(f"SELECT FROM bonds WHERE {what} = {criteria}")
