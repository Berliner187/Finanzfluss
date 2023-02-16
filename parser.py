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
from bs4 import BeautifulSoup
import requests
import os
import re
from csv import DictWriter, DictReader
from ast import literal_eval

from db_manager import DataBaseManager
FILE_RESPONSE = f'tmp/response_from_moex.dat'
fields_response = ['ticker', 'profitability', 'maturity_date', 'coupon_amount', 'payment_date']


PARSER_TABLE_NAME = 'parser'
PARSER_TABLE = """
    CREATE TABLE parser (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        profitability TEXT,
        maturity_date TEXT,
        coupon_amount TEXT,
        payment_date TEXT
    )
"""


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686; en-GB) Gecko/20070619 Firefox/108.0esr'
}

# Подключение базы данных
# data_base = DataBaseManager()
# data_base.create_table('bonds.db', PARSER_TABLE_NAME)


if os.path.exists(FILE_RESPONSE) is False:
    with open(FILE_RESPONSE, mode="a", encoding='utf-8') as data:
        logg_writer = DictWriter(data, fieldnames=fields_response, delimiter=';')
        logg_writer.writeheader()


class ResponseResultMOEX:
    def __init__(self, isin):
        self.isin = isin

    def get_info(self):
        global FILE_RESPONSE
        global fields_response

        url = f'https://www.moex.com/ru/issue.aspx?board=TQCB&code={self.isin}'

        profit, maturity_date, coupon, coupon_payment_date = [], [], [], []

        def template_get_content(element):
            if '</b>' in element:
                element = element.replace('<b>', '')
            elif '</b>' in element:
                element = element.replace('</b>', '')
            return ' '.join(re.findall(r'>([^><]+)<', element))

        def read_saved_data():
            # Возвращает все сохраненные бумаги
            dict_ = {}
            array_ = []
            with open(FILE_RESPONSE, encoding='utf-8') as file_response:
                reader = DictReader(file_response, delimiter=';')
                for row in reader:
                    dict_['ticker'] = row['ticker']
                    dict_['profitability'] = row['profitability']
                    dict_['maturity_date'] = row['maturity_date']
                    dict_['coupon_amount'] = row['coupon_amount']
                    dict_['payment_date'] = row['payment_date']
                    array_.append(dict_)
                    dict_ = {}
            return array_

        def get_saved_tickers():
            ## Возвращает True/False.
            # False - бумага не была сохранена ранее
            # True - бумага была сохранена ранее
            array_saved_tickers = []
            with open(FILE_RESPONSE, encoding='utf-8') as file_response:
                reader = DictReader(file_response, delimiter=';')
                for row in reader:
                    array_saved_tickers.append(row['ticker'])
            if self.isin in array_saved_tickers:
                return True
            else:
                return False

        def get_needed_data_by_ticker():
            # Возвращает все сохраненные данные о бумаге
            for dict_ in read_saved_data():
                if dict_['ticker'] == self.isin:
                    profit.append(literal_eval(dict_['profitability'])[0])
                    profit.append(literal_eval(dict_['profitability'])[1])
                    maturity_date.append(literal_eval(dict_['maturity_date'])[0])
                    maturity_date.append(literal_eval(dict_['maturity_date'])[1])
                    coupon.append(literal_eval(dict_['coupon_amount'])[0])
                    coupon.append(literal_eval(dict_['coupon_amount'])[1])
                    coupon_payment_date.append(literal_eval(dict_['payment_date'])[0])
                    coupon_payment_date.append(literal_eval(dict_['payment_date'])[1])

        def get_data_from_moex():
            # Получение данных с МосБиржи
            full_page = requests.get(url=url, headers=headers)
            soup = BeautifulSoup(full_page.text, 'html.parser')
            array_received_info = []
            for page_data in soup.find_all('tr'):
                for i in page_data:
                    if i != '\n':
                        array_received_info.append(i)
            for elem in range(len(array_received_info)):
                if '?' not in template_get_content(str(array_received_info[elem])):
                    if 'Доходность' in array_received_info[elem]:
                        profit.append(template_get_content(str(array_received_info[elem])))
                        profit.append(template_get_content(str(array_received_info[elem + 1])))
                    elif 'Дата погашения' in array_received_info[elem]:
                        maturity_date.append(template_get_content(str(array_received_info[elem])))
                        maturity_date.append(template_get_content(str(array_received_info[elem + 1])))
                    elif 'Дата выплаты купона' in str(array_received_info[elem]):
                        coupon_payment_date.append(template_get_content(str(array_received_info[elem])))
                        coupon_payment_date.append(template_get_content(str(array_received_info[elem + 1])))
                    elif 'Сумма купона' in str(array_received_info[elem]):
                        coupon.append(template_get_content(str(array_received_info[elem])))
                        coupon.append(template_get_content(str(array_received_info[elem + 1])))
            return profit, maturity_date, coupon_payment_date, coupon

        def write_bond_data():
            try:
                with open(FILE_RESPONSE, encoding='utf-8', mode='a') as data_writer:
                    response_writer = DictWriter(data_writer, fieldnames=fields_response, delimiter=';')
                    response_writer.writerow({
                        'ticker': self.isin,
                        'profitability': profit,
                        'maturity_date': maturity_date,
                        'coupon_amount': coupon,
                        'payment_date': coupon_payment_date,
                    })
                    data_writer.close()
                print('\nФайл создан, данные записаны')
            except Exception as e:
                print('\nОшибка записи:', e)

        if get_saved_tickers() is False:
            get_data_from_moex()
            write_bond_data()
        else:
            get_needed_data_by_ticker()

        return profit, maturity_date, coupon_payment_date, coupon


# mx-security-description
# ResponseResultMOEX('RU000A105GV6').get_info()
