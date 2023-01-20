# -*- coding: UTF-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager
import bonds
from bonds import COLUMNS_TABLE_BONDS
from bonds import RequestProcessingInDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from time import sleep
import parser

import auth


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'ev8wvg9dvhsvsklvnsdjvn'


NAME_APP = 'Finanzfluss'


CATEGORIES_WASTES = []
CATEGORIES_RECEIPTS = []

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


@app.route('/bonds', methods=['POST', 'GET'])
def assets():
    if request.method == 'POST':
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
        # Запись облигации в базу данных
        RequestProcessingInDataBase.add_bond(tuple(array_result_transmitted_data))
        # bond_info = parser.InfoBond(request.form.get('ticker'))

    # Данные для отображения
    bond = bonds.SummaryAnalysisBondsOfIndicators()

    # Скрытые данные
    array_hidden_data = []
    for item in bond.return_saved_bonds_for_display():
        array_hidden_data.append(parser.InfoBond(item[1]).get_ingo())
    print(array_hidden_data)
    # Данные для календаряF
    calendar_array = []
    calendar_dict = {}
    try:
        for i in range(len(array_hidden_data)):
            calendar_dict['date'] = array_hidden_data[i][3][1]
            calendar_dict['name'] = bond.return_saved_bonds_for_display()[i][2]
            calendar_dict['coupon'] = round(float(
                bond.return_saved_bonds_for_display()[i][6].replace(',', '.')) * bond.return_saved_bonds_for_display()[i][5], 2)

            calendar_array.append(calendar_dict)
            calendar_dict = {}
    except TypeError:
        pass

    print(calendar_array)
    calendar_array.sort(key=lambda dictionary: dictionary['date'])

    return render_template(
        'assets.html',
        bond_array=bond.return_saved_bonds_for_display(),
        summary_portfolio=bond.calculate_the_total_return_of_the_portfolio(),
        summary_price=bond.return_summary_price_for_display(),
        profitability_per_year=bond.profitability_per_year_for_display(),
        profit_to_the_end=bond.calculation_of_all_references_to_the_end(),
        profitability_per_year_by_sem_positions=bond.profitability_per_year_by_sem_positions_for_display(),
        array_hidden_data=array_hidden_data,
        calendar_array=calendar_array
    )


@app.route('/bonds/delete/<int:bond_id>')
def delete_bond(bond_id):
    print('Запущено: delete_bond')
    try:
        RequestProcessingInDataBase.delete_record(bond_id)
        return redirect("/bonds")
    except:
        return "Ошибка при удалении"


@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(error):
    split_error = str(error).split(':')
    return render_template('error.html', error_code=split_error[0], error_text=split_error[1])


if __name__ == '__main__':
    app.run(host='192.168.175.236', port=5000, debug=False)
