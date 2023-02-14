# -*- coding: UTF-8 -*-
"""
    Модуль расчета облигаций

    Finanzfluss - Finance Flow App
    Приложение позволяет управлять денежными потоками, рассчитывать доход от активов,
    а также анализировать транзакции
    Copyright (C) 2023 by Berliner187

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
"""
from db_manager import DataBaseManager
from parser import ResponseResultMOEX
# UNIQUE ON CONFLICT IGNORE

BONDS_DATA_BASE = 'bonds.db'
BONDS_TABLE_NAME = 'bonds'
BONDS_TABLE = """CREATE TABLE IF NOT EXISTS bonds (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    ticker TEXT,
    bond TEXT,
    nominal INTEGER,
    average_price REAL,
    quantity INTEGER,
    coupon_value REAL,
    aci REAL,
    number_of_payments_per_year INTEGER,
    total_payments INTEGER,
    date_of_purchase TEXT
)"""

BONDS_TABLE_EXECUTE = f"INSERT INTO {BONDS_TABLE_NAME} (ticker, bond, nominal, average_price, " \
                      f"quantity, " \
                      f"coupon_value, " \
                      f"aci," \
                      f"number_of_payments_per_year, " \
                      f"total_payments, " \
                      f"date_of_purchase) " \
                      f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" \

COLUMNS_TABLE_BONDS = [
    'id',
    'ticker',
    'bond',
    'nominal',
    'average_price',
    'quantity',
    'coupon_value',
    'aci',
    'number_of_payments_per_year',
    'total_payments',
    'date_of_purchase'
]

# Подключение базы данных
data_base = DataBaseManager()
data_base.create_table(BONDS_DATA_BASE, BONDS_TABLE)


class FormatNumber:
    """
        self.number - integer/float number
        self.type_number - cur=currency, per=percent:
    """
    def __init__(self, type_number):
        self.type_number = type_number

    def get_format(self, number):
        def format_number(yum):
            return '{0:,}'.format(yum).replace(',', ' ').replace('.', ',')

        if self.type_number == 'cur':
            return f'{format_number(number)} ₽'

        elif self.type_number == 'per':
            return f'{format_number(number)} %'

        else:
            return format_number(number)


class Bonds:
    """
        TICKER (ISIN) - Тикер облигации
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
    def __init__(self, data_bond):
        self.id = data_bond[0]
        self.ticker = data_bond[1]
        self.bond = data_bond[2]
        self.nominal = data_bond[3]
        self.average_price = data_bond[4]
        self.quantity = data_bond[5]
        self.coupon_value = data_bond[6]
        self.aci = data_bond[7]
        self.number_of_payments_per_year = data_bond[8]
        self.total_payments = data_bond[9]
        self.date_of_purchase = data_bond[10]

    def date(self):
        return

    # Расчет купонного дохода
    def calculate_coupon_profit(self, quantity_payments):
        coupon_income = (self.coupon_value * self.quantity) * quantity_payments
        return coupon_income

    # Доходность в процентах
    def calculate_percent_profitability(self, profit):
        # Расчет доходности в процентах
        return round(profit * 100 / (self.average_price * self.quantity), 2)

    # Расчет общего дохода к дате погашения
    def calculate_all_profitability(self):
        difference_nominal = (self.nominal - self.average_price) * self.quantity
        coupon_income = self.calculate_coupon_profit(self.total_payments)
        profit = round(difference_nominal + coupon_income, 2)
        percent_profitability = round(self.calculate_percent_profitability(profit), 2)
        return profit, percent_profitability

    # Расчет доходности к концу
    def calculate_profitability_per_year(self):
        # !!! ДУБЛЕР !!!
        # Расчет годового дохода
        # ДОХОД В РУБЛЯХ, ДОХОД В ПРОЦЕНТАХ
        coupon_income = (self.coupon_value * self.quantity) * self.number_of_payments_per_year
        invested = (self.average_price * self.quantity)
        coupon_income = round(coupon_income, 2)
        profit_percent = round(coupon_income * 100 / invested, 2)
        return coupon_income, profit_percent

    def calculate_profitability_per_year_for_display(self):
        coupon_income = SummaryAnalysisBondsOfIndicators.format_number(self.calculate_profitability_per_year()[0])
        profit_percent = SummaryAnalysisBondsOfIndicators.format_number(self.calculate_profitability_per_year()[1])
        return f"{coupon_income} ₽ • ({profit_percent} %)"

    def get_profitability_to_end_for_display(self):
        profit = SummaryAnalysisBondsOfIndicators.format_number(self.calculate_all_profitability()[0])
        percent_profitability = SummaryAnalysisBondsOfIndicators.format_number(self.calculate_all_profitability()[1])
        return f"{profit} ₽ • ({percent_profitability} %)"

    # Получение суммарной стоимости бумаг на момент покупки
    def get_summary_price(self):
        return round(self.average_price * self.quantity, 2)

    def get_summary_price_for_display(self):
        return FormatNumber('cur').get_format(self.get_summary_price())

    # Получение доли бумаги в портфеле
    def get_share_in_portfolio(self):
        bond_instance = SummaryAnalysisBondsOfIndicators()
        summary_invested_array = bond_instance.return_summary_price()
        summary_invested = sum(summary_invested_array)
        return round(self.get_summary_price() * 100 / summary_invested, 2)

    # Суммарно вложено (первоначальная стоимость в портфеле)
    @staticmethod
    def calculate_summary_price():
        # !!! ДУБЛЕР !!!
        array_summary_price = []
        saved_bonds_array = SummaryAnalysisBondsOfIndicators.return_saved_bonds()
        for bond_from_array in saved_bonds_array:
            price = round((bond_from_array[4] * bond_from_array[5]) + bond_from_array[7], 2)
            array_summary_price.append(price)
        return array_summary_price

    def get_profitability_per_month(self):
        profit = self.coupon_value * self.quantity  # Годовой доход
        if self.number_of_payments_per_year == 2:
            return round(profit * 2 / 12, 2)
        elif self.number_of_payments_per_year == 4:
            return round(profit * 4 / 12, 2)
        elif self.number_of_payments_per_year == 12:
            return round(profit, 2)
        else:
            return 0

    def get_profitability_per_month_for_display(self):
        if self.number_of_payments_per_year != 12: tilda = '~'
        else: tilda = ''
        return f'{tilda}{SummaryAnalysisBondsOfIndicators.format_number(round(self.get_profitability_per_month(), 2))} ₽'

    def get_profitability_per_quarter(self):
        if self.number_of_payments_per_year == 4:
            return self.coupon_value * self.quantity
        elif self.number_of_payments_per_year == 2:
            return (self.coupon_value * self.quantity) / 2
        elif self.number_of_payments_per_year == 12:
            return (self.coupon_value * self.quantity) * 3
        else:
            return 0

    def get_profitability_per_half_year(self):
        result = 0
        if self.number_of_payments_per_year == 4:
            result = (self.coupon_value * self.quantity) / 2
        elif self.number_of_payments_per_year == 2:
            result = self.coupon_value * self.quantity
        elif self.number_of_payments_per_year == 12:
            result = (self.coupon_value * self.quantity) * 6
        return round(result, 2)

    def get_profitability_per_quarter_for_display(self):
        return SummaryAnalysisBondsOfIndicators.format_number(round(self.get_profitability_per_quarter(), 2)) + ' ₽'

    def get_profitability_per_half_year_for_display(self):
        return FormatNumber('cur').get_format(self.get_profitability_per_half_year())

    def about_bond_indicators(self):
        profitability_per_quarter = 0
        profitability_per_year = 0

        db = DataBaseManager()
        # data_bond = db.select_row_from_table(BONDS_DATA_BASE, BONDS_TABLE_NAME, '*', 'ticker', ticker)

        profitability_per_year = self.calculate_profitability_per_year()
        return

    # Расчет разницы номинала и цены при покупке
    def get_nominal_value_difference(self):
        return round((self.nominal * self.quantity) - (self.average_price * self.quantity), 2)

    def get_nominal_value_difference_for_display(self):
        return FormatNumber('cur').get_format(self.get_nominal_value_difference())

    def get_tax_per_year(self):
        profit = self.calculate_profitability_per_year()[0]
        return round(profit * 0.13, 2)

    def get_tax_per_year_for_display(self):
        return FormatNumber("cur").get_format(self.get_tax_per_year())

    def nominal_profitability(self):
        return round((self.coupon_value * 100 / self.nominal) * self.number_of_payments_per_year, 2)


class SummaryAnalysisBondsOfIndicators:
    """
        Суммарная аналитика показателей всех сохраненных ценных бумаг.
        Данные выгружаются из базы данных.
    """

    # Форматирование чисел (только для вывода)
    @staticmethod
    def format_number(number):
        return '{0:,}'.format(number).replace(',', ' ').replace('.', ',')

    @staticmethod
    def return_saved_bonds():
        array_saved_bonds = []
        for item in data_base.select_from_table(BONDS_DATA_BASE, BONDS_TABLE_NAME, "*"):
            array_saved_bonds.append(list(item))
        return array_saved_bonds

    # Отображение сохраненных облигаций
    def return_saved_bonds_for_display(self):
        array_saved_bonds = self.return_saved_bonds()
        format_array_saved_bonds = []
        for i in range(len(array_saved_bonds)):
            array_saved_bonds[i][4] = self.format_number(array_saved_bonds[i][4])
            array_saved_bonds[i][6] = self.format_number(array_saved_bonds[i][6])
            array_saved_bonds[i][7] = self.format_number(array_saved_bonds[i][7])
            format_array_saved_bonds.append(array_saved_bonds[i])
        return array_saved_bonds

    # Получение данных конкретной облигаций
    def get_bond_info(self):
        return self.return_saved_bonds()

    # Годовая доходность
    def return_profitability_per_year(self):
        array_coupon_income = []
        array_profit_percent = []
        array_saved_bonds = self.return_saved_bonds()
        for item in array_saved_bonds:
            coupon_income = (item[6] * item[5]) * item[8]
            invested = (item[4] * item[5])
            profit_percent = round(coupon_income * 100 / invested, 2)
            array_coupon_income.append(round(coupon_income, 2))
            array_profit_percent.append(round(profit_percent, 2))
        return [array_coupon_income, array_profit_percent]

    # Формат годовой доходности для отображения
    def profitability_per_year_for_display(self):
        profitability_in_currency, profitability_in_percent = [], []
        # Доходность в рублях
        for item in self.return_profitability_per_year()[0]:
            profitability_in_currency.append(self.format_number(item))
        # Доходность в процентах
        for item in self.return_profitability_per_year()[1]:
            profitability_in_percent.append(self.format_number(item))
        return [profitability_in_currency, profitability_in_percent]

    # Годовой доход по всем позициям
    def profitability_per_year_by_sem_positions(self):
        summary = 0
        array_coupon_income = self.return_profitability_per_year()
        for profit in array_coupon_income[0]:
            summary += profit
        return summary

    def profitability_per_year_by_sem_positions_for_display(self):
        summary_profit = self.profitability_per_year_by_sem_positions()
        summary_invested = 0
        for i in self.return_summary_price():
            summary_invested += i
        try:
            profit_percent = round(summary_profit * 100 / summary_invested, 2)
            summary_profit = round(summary_profit, 2)
            # Форматирование чисел
            summary_profit = self.format_number(summary_profit)
            profit_percent = self.format_number(profit_percent)
            return f'{summary_profit} ₽ • {profit_percent} % — за год'
        except ZeroDivisionError:
            return '-'

    # Суммарно вложено
    def return_summary_price(self):
        array_summary_price = []
        saved_bonds_array = self.return_saved_bonds()
        for bond_from_array in saved_bonds_array:
            price = round((bond_from_array[4] * bond_from_array[5]) + bond_from_array[7], 2)
            array_summary_price.append(price)
        return array_summary_price

    # Суммарно вложено (для отображения)
    def return_summary_price_for_display(self):
        array_summary_price = self.return_summary_price()
        format_array_summary_price = []
        for price in array_summary_price:
            price = self.format_number(price)
            format_array_summary_price.append(price)
        return format_array_summary_price

    @staticmethod
    def return_profit():
        array = []
        for bond_from_db in data_base.select_from_table(BONDS_DATA_BASE, BONDS_TABLE_NAME, "*"):
            instance_bond_from_db = Bonds(bond_from_db)
            array.append(instance_bond_from_db.calculate_all_profitability())
        return array

    @staticmethod
    def calculate_all_profit():
        array_profit, array_percent_profit = [], []
        for bond_data in data_base.select_from_table(BONDS_DATA_BASE, BONDS_TABLE_NAME, "*"):
            calculate_profit = Bonds(bond_data)
            profit, percent_profit = calculate_profit.calculate_all_profitability()
            array_profit.append(profit)
            array_percent_profit.append(percent_profit)
        return array_profit, array_percent_profit

    def calculation_of_all_references_to_the_end(self):
        # Расчет доходности в рублях
        summary_profit, difference_nominal = 0, 0
        for bond_data in data_base.select_from_table(BONDS_DATA_BASE, BONDS_TABLE_NAME, "*"):
            bond = Bonds(bond_data)
            difference_nominal += bond.get_nominal_value_difference()
            profit, percent_profit = bond.calculate_all_profitability()
            summary_profit += (profit + difference_nominal)
        summary_profit = round(summary_profit, 2)
        # Всего вложено
        summary_invested = 0
        array_summary_price = self.return_summary_price()
        for price in array_summary_price:
            summary_invested += price
        try:
            # Расчет доходности в процентах
            profit_percent = round(summary_profit * 100 / summary_invested, 2)
            # Форматирование чисел
            summary_profit = self.format_number(summary_profit)
            profit_percent = self.format_number(profit_percent)
            return f'{summary_profit} ₽ • {profit_percent} % — к концу'
        except ZeroDivisionError:
            return '-'

    # Расчет стоимости бумаг в портфеле
    def calculate_the_total_return_of_the_portfolio(self):
        average_prices_array, quantities_array, aci_total_array = [], [], []
        summary = 0

        # Добавление необходимых параметров в массив для расчета вложенных средств
        def add_parameter_in_array(column_name, array):
            for elem in data_base.select_from_table(BONDS_DATA_BASE, BONDS_TABLE_NAME, column_name):
                array.append(float("".join(map(str, elem))))

        # Суммарная рыночная стоимость при покупке
        add_parameter_in_array('average_price', average_prices_array)
        # Суммарное количество в портфеле
        add_parameter_in_array('quantity', quantities_array)
        # Суммарный НКД при покупке
        add_parameter_in_array('aci', aci_total_array)

        # Расчет вложенных средств
        for price, quantity, aci in zip(average_prices_array, quantities_array, aci_total_array):
            summary += (price * quantity) + aci

        return round(summary, 2)


class RequestProcessingInDataBase:
    @staticmethod
    def add_bond(data_bond):
        data_base.write_in_table(BONDS_DATA_BASE, BONDS_TABLE_EXECUTE, data_bond)

    @staticmethod
    def delete_record(criteria):
        data_base.delete_record(BONDS_DATA_BASE, criteria)


class BondsController:
    """
        Отображение данных во фреймах.
        Является связующим звеном между View и Model
    """

    @staticmethod
    def get_bond_info(ticker):
        # Выгрузка из БД
        db = DataBaseManager()
        return db.select_row_from_table(BONDS_DATA_BASE, BONDS_TABLE_NAME, '*', 'ticker', ticker)

    def bonds_frame(self):
        # Данные для отображения
        bond = SummaryAnalysisBondsOfIndicators()

        ## Вызов классов
        # Класс Format для форматирования строк
        format_currency = FormatNumber('cur')

        # Данные внутри контейнера с облигацией (при раскрытии)
        array_hidden_data = []
        for item in bond.return_saved_bonds():
            data = ResponseResultMOEX(item[1]).get_info()
            data[3][1] = format_currency.get_format(float(data[3][1]))
            array_hidden_data.append(data)
        # Данные для календаря
        calendar_array = []
        try:
            calendar_dict = {}
            for i in range(len(array_hidden_data)):

                calendar_dict['date'] = array_hidden_data[i][2][1]
                calendar_dict['name'] = bond.return_saved_bonds()[i][2]
                calendar_dict['coupon'] = format_currency.get_format(
                    bond.return_saved_bonds()[i][5] * bond.return_saved_bonds()[i][6])

                calendar_array.append(calendar_dict)
                calendar_dict = {}
        except TypeError or IndexError:
            pass

        # Костыль
        calendar_array.sort(key=lambda dictionary: dictionary['date'][0:2])
        calendar_array.sort(key=lambda dictionary: dictionary['date'][3:5])

        label_portfolio = {
            'Портфель': format_currency.get_format(bond.calculate_the_total_return_of_the_portfolio()),
        }

        label_profitability = {
            'Доходность': [
                bond.profitability_per_year_by_sem_positions_for_display(),
                bond.calculation_of_all_references_to_the_end()
            ],
        }

        label_calendar = {
            'Календарь': calendar_array
        }

        return label_portfolio, label_profitability, label_calendar

    # Страница с детальной информацией о бумаге
    def about_bond(self, ticker):
        ## Данные о бумаге из БД
        bond = self.get_bond_info(ticker)

        ## Вызов классов
        # Класс Bonds для вычислений
        calculation = Bonds(bond)
        # Класс Format для форматирования строк
        format_currency = FormatNumber('cur')
        format_percent = FormatNumber('per')

        ### ЛЕЙБЛ: ШАПКА ###
        label_head = {
            'ticker': ticker,
            'name': bond[2],
            'total_invested': format_currency.get_format(calculation.get_summary_price()),
            'share_in_portfolio': format_percent.get_format(calculation.get_share_in_portfolio())
        }

        ### ЛЕЙБЛ: О ВЫПУСКЕ ###
        # Получение данных с MOEX: (доходность), дата погашения, даты выплаты купона, величина купона
        response_from_moex = list(ResponseResultMOEX(ticker).get_info())
        # Костыль
        response_from_moex[3][1] = format_currency.get_format(float(response_from_moex[3][1]))
        about_the_release_data = {
            'maturity_date': response_from_moex[1],
            'coupon_payment_date': response_from_moex[2],
            'coupon_amount': response_from_moex[3],
            'nominal': ['Номинал', format_currency.get_format(bond[3])],
            'payments_per_year': ['Выплат в год', bond[8]],
            'payments_left': ['Осталось выплат', bond[9]],
            'nominal_profitability':
                ['Номинальная доходность', format_percent.get_format(calculation.nominal_profitability())],
            'current_profitability': response_from_moex[0],
        }

        ### ЛЕЙБЛ: ПОКАЗАТЕЛИ ###
        indicators = {
            'aci': ['Накопленный купонный доход', '-'],
            'difference_nominal_and_price':
                ['Разность номинала и цены', calculation.get_nominal_value_difference_for_display()],
            'monthly_income': ['Доход за месяц', calculation.get_profitability_per_month_for_display()],
            'income_per_quarter': ['Доход за квартал', calculation.get_profitability_per_quarter_for_display()],
            'income_per_half_year': ['Доход за полгода', calculation.get_profitability_per_half_year_for_display()],
            'income_per_year': ['Доходность за год', calculation.calculate_profitability_per_year_for_display()],
            'profitability_to_maturity_date':
                ['Доходность к дате погашения', calculation.get_profitability_to_end_for_display()],
            'tax_per_year':
                ['Предварительный годовой налог', calculation.get_tax_per_year_for_display()],
        }

        ### ЛЕЙБЛ: В ПОРТФЕЛЕ ###
        in_portfolio = {
            'average_price': ['Цена', format_currency.get_format(bond[4])],
            'quantity': ['Количество', f'{bond[5]} шт.']
        }

        return label_head, about_the_release_data, indicators, in_portfolio
