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
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager
import bonds
from bonds import COLUMNS_TABLE_BONDS
from bonds import RequestProcessingInDataBase
from werkzeug.security import generate_password_hash, check_password_hash
import parser

import auth

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'ev8wvg9dvhsvsklvnsdjvn'

NAME_APP = 'Finanzfluss'

CATEGORIES_WASTES, CATEGORIES_RECEIPTS = [], []

""" 
    КАТЕГОРИИ ТРАНЗАКЦИЙ
"""


# WASTES = 'files/wastes.dat'
# RECEIPTS = 'files/receipts.dat'
#
# def refill_categories(file_type_transaction, array_type_transaction):
#     file = open(file_type_transaction, encoding='utf-8')
#     file_data = file.readlines()
#     for category in file_data:
#         array_type_transaction.append(category)
#
# refill_categories(WASTES, CATEGORIES_WASTES)
# refill_categories(RECEIPTS, CATEGORIES_RECEIPTS)


@app.route('/login', methods=["POST", "GET"])
def login():
    title = 'Вход'
    right_redirect = '/signup'
    right_text = 'Зарегистрироваться'
    if request.method == "POST":
        user_login = request.form.get('login')
        user_password = request.form.get('password')

    return render_template('login.html',
                           name_app=NAME_APP,
                           title=title,
                           right_redirect=right_redirect,
                           right_text=right_text)


@app.route('/signup', methods=["POST", "GET"])
def signup():
    title = 'Регистрация'
    right_redirect = '/login'
    right_text = 'Войти'
    if request.method == "POST":
        user_login = request.form.get('login')
        user_password = request.form.get('password')
        user_confirm_password = request.form.get('confirm_password')

        # Проверка на дубликат пользователя
        statement = False
        users_from_db = auth.Users.select_from_table()
        for i in users_from_db:
            if user_login == i[1]:
                statement = True

        if login == '':
            flash("Введите логин", category='error')
        elif user_password == '':
            flash("Введите пароль", category='error')
        else:
            if statement is False:
                if (user_password == user_confirm_password) and (len(request.form['login']) > 2):
                    array_result_transmitted_data = []
                    columns = auth.COLUMNS_TABLE_USERS.copy()[1:]
                    for column in columns:
                        array_result_transmitted_data.append(request.form.get(column))
                    auth.Users.save_new_user(tuple(array_result_transmitted_data))
                    # flash("Успешно!", category='success')
                    return redirect('/')
                else:
                    flash("Пароли не совпадают", category='error')
            else:
                flash("Логин занят", category='error')
    return render_template('signup.html',
                           name_app=NAME_APP,
                           title=title,
                           right_redirect=right_redirect,
                           right_text=right_text)


@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html')


@app.route('/assets')
def assets_blyat():
    bond = bonds.SummaryAnalysisBondsOfIndicators()
    bonds_controller = bonds.BondsController()

    return render_template(
        'assets.html',
        name_app=NAME_APP,
        title='Активы',
        header_link='Войти',
        header_redirect='/login',
        bonds_assets=bonds_controller.bonds_frame(),
        amount_in_portfolio=bond.calculate_the_total_return_of_the_portfolio(),
        profitability_per_year=bond.profitability_per_year_by_sem_positions_for_display(),
        profitability_total=bond.calculation_of_all_references_to_the_end(),
        take_profit=0
    )


@app.route('/assets/bonds', methods=['POST', 'GET'])
def assets():
    if request.method == 'POST':
        # Получение параметров облигации
        array_result_transmitted_data = []
        columns = COLUMNS_TABLE_BONDS.copy()[1:]
        cnt = 0
        for column in columns:
            if cnt in [3, 5, 6]:
                array_result_transmitted_data.append(float(request.form.get(column)))
            elif cnt in [4, 7, 8]:
                array_result_transmitted_data.append(int(request.form.get(column)))
            else:
                array_result_transmitted_data.append(str(request.form.get(column)))
            cnt += 1
        # Запись данных об облигации в базу данных
        RequestProcessingInDataBase.add_bond(tuple(array_result_transmitted_data))

    # Данные для отображения
    bond = bonds.SummaryAnalysisBondsOfIndicators()
    bonds_controller = bonds.BondsController()

    # Скрытые данные
    array_hidden_data = []
    for item in bond.return_saved_bonds_for_display():
        data = parser.ResponseResultMOEX(item[1]).get_info()
        ### Костыль
        # Форматирование суммы купона
        data[3][1] = bonds.FormatNumber('cur').get_format(float(data[3][1]))
        array_hidden_data.append(data)

    return render_template(
        'bonds.html',
        bond_array=bond.return_saved_bonds_for_display(),
        summary_price=bond.return_summary_price_for_display(),
        profitability_per_year=bond.profitability_per_year_for_display(),
        array_hidden_data=array_hidden_data,
        bonds_frame=bonds_controller.bonds_frame()
    )


@app.route('/assets/bonds/delete/<int:bond_id>')
def delete_bond(bond_id):
    print('Запущено: delete_bond')
    try:
        RequestProcessingInDataBase.delete_record(bond_id)
        return redirect("/assets/bonds")
    except Exception as e:
        split_error = "Ошибка при удалении: Не удалось удалить облигацию из базы данных."
        return render_template('error.html', error_code=split_error[0], error_text=split_error[1])


@app.route('/assets/bonds/about/<string:ticker>')
def about_bond(ticker):
    bond_info = bonds.SummaryAnalysisBondsOfIndicators()
    bonds_all = bond_info.get_bond_info()

    # Поиск данных об облигации из БД
    found_bond = []
    for search_bond in bonds_all:
        if search_bond[1] == ticker:
            found_bond = search_bond

    # Экземпляр класса Контроллер, управляет бизнес-моделью и видом
    info_by_labels = bonds.BondsController()

    return render_template(
        'about-bond.html',
        name_app=NAME_APP,
        title=found_bond[2],
        header_link='Войти',
        header_redirect='/login',
        info_about_bond=info_by_labels.about_bond(ticker)
    )


@app.route('/about')
def about():
    return render_template('about.html',
                           name_app=NAME_APP,
                           title='О сервисе',
                           header_link='Войти',
                           header_redirect='/login')


@app.route('/licence')
def licence():
    return render_template('licence.html', name_app=NAME_APP, title='Лицензия')


@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(error):
    split_error = str(error).split(':')
    return render_template('error.html', error_code=split_error[0], error_text=split_error[1])


if __name__ == '__main__':
    # app.run(host='192.168.1.9', port=5000, debug=False)
    app.run(host='192.168.31.204', port=5000, debug=False)
