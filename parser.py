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


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686; en-GB) Gecko/20070619 Firefox/108.0esr'
}


class ResponseResultMOEX:
    def __init__(self, ticker):
        self.bond = ticker

    def get_info(self):
        file = f'tmp/{self.bond}.dat'
        url = f'https://www.moex.com/ru/issue.aspx?board=TQCB&code={self.bond}'

        profit, maturity_date, coupon, coupon_payment_date = [], [], [], []

        if os.path.exists(file):
            with open(file, 'r', encoding='UTF=8') as read_pars_data:
                array = read_pars_data.readlines()

            def template_get_content(element):
                return ' '.join(re.findall(r'>([^><]+)<', element))

            data = array
            for elem in range(len(data)):
                if '?' not in template_get_content(data[elem]):
                    if 'Доходность' in data[elem]:
                        profit.append(template_get_content(data[elem]))
                        profit.append(template_get_content(data[elem + 1]))
                    elif 'Дата погашения' in data[elem]:
                        maturity_date.append(template_get_content(data[elem]))
                        maturity_date.append(template_get_content(data[elem + 1]))
                    elif 'Сумма купона' in data[elem]:
                        coupon.append(template_get_content(data[elem]))
                        coupon.append(template_get_content(data[elem + 1]))
                    elif 'Дата выплаты купона' in data[elem]:
                        coupon_payment_date.append(template_get_content(data[elem]))
                        coupon_payment_date.append(template_get_content(data[elem + 1]))

            return profit, maturity_date, coupon_payment_date, coupon

        else:
            try:
                full_page = requests.get(url=url, headers=headers)
                soup = BeautifulSoup(full_page.text, 'html.parser')
                array = []
                for data in soup.find_all('tr'):
                    array.append(data)
                    print(data)
                with open(file, 'w', encoding='UTF=8') as write_pars_data:
                    write_pars_data.write(str(array))
                    write_pars_data.close()
                print('\nФайл создан, данные записаны')
            except Exception as e:
                print('Ошибка записи\n')
                print(e)
