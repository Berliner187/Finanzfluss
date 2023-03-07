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
from werkzeug.security import generate_password_hash, check_password_hash
import random
import parser

import auth
import bonds
import db_manager

from bonds import COLUMNS_TABLE_BONDS
from bonds import RequestProcessingInDataBase


app = Flask(__name__)
app.config.from_object(__name__)
symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
random_symbols = ''
for i in range(16):
    random_symbols = random.choice(symbols)
app.config['SECRET_KEY'] = random_symbols

NAME_APP = 'Finanzfluss'


@app.route('/login', methods=["POST", "GET"])
def login():
    title = 'Вход'
    right_redirect = '/signup'
    right_text = 'Зарегистрироваться'

    user_login = request.form.get('login')
    user_password = request.form.get('password')

    if user_login and user_password:
        # Проверка на существование пользователя
        statement = False

        found_user = []
        users_from_db = auth.Users.select_from_table()
        for user in users_from_db:
            if user_login == user[1]:
                statement = True
                found_user = user
        if statement:
            print(found_user)
    else:
        return render_template('login.html')

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
        for user in users_from_db:
            if user_login == user[1]:
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


@app.route('/assets/what-are-bonds')
def what_are_bonds():
    what_are_bonds_text = {
        'Что такое облигации': [
            'Облигации – это ценные бумаги, которые выпускаются государством или компанией для привлечения средств на развитие или текущую деятельность.',
            'Облигации являются одним из наиболее распространенных инструментов инвестирования, который позволяет зарабатывать на разнице между ценой покупки и продажи ценных бумаг, а также на выплачиваемых процентах.',
            'Одним из основных параметров облигаций является купонная ставка, которая представляет собой процент, выплачиваемый инвестору за пользование его деньгами. Также важным параметром является срок облигации, который определяет, через какой период времени произойдет ее погашение и инвестор получит обратно вложенные средства.'
        ]
    }

    text_dict = {
        'Сравнение со вкладами':
            [
                'Вклады – это банковские продукты, при которых клиент вкладывает свои средства на определенный срок с определенной процентной ставкой. В отличие от облигаций, вклады выпускаются банками и не представляют собой ценные бумаги.',
                'Одним из основных отличий между облигациями и вкладами является риск. Облигации имеют риск дефолта (невозврата долга), который зависит от кредитного рейтинга эмитента. Чем ниже кредитный рейтинг, тем выше риск дефолта, и соответственно, тем выше процентная ставка по облигации. Вклады, с другой стороны, защищены государственной страховкой вкладов, и клиенты могут быть уверены в том, что получат свои вложенные средства назад, даже если банк обанкротится.',
                'Еще одним отличием является ликвидность. Облигации могут быть проданы на бирже или через банковский депозитарий, что делает их достаточно ликвидными. Однако, если продать облигацию до истечения ее срока, то инвестор может не получить полную сумму вложенных средств. Вклады, в свою очередь, являются малоликвидными инструментами, и при досрочном снятии инвестор может потерять часть полученных процентов.'
            ],
        'Сравнение с акциями':
            [
                'Акции - это ценные бумаги, которые представляют собой долю в собственности компании. Купив акцию, инвестор становится совладельцем компании и имеет право на получение дивидендов (часть прибыли компании, которая распределяется между акционерами) и участие в принятии стратегических решений. Однако, при покупке акций инвестор также несет риски потери инвестиций, так как цена акций может снижаться в результате различных факторов, таких как экономическая ситуация, финансовые результаты компании, изменения в отрасли и т.д.',
                'Одно из основных отличий между облигациями и акциями заключается в том, что облигации представляют собой долговые инструменты, тогда как акции – это долевые инструменты. Облигации выпускаются компаниями или правительством, которые занимают деньги у инвесторов и обещают вернуть их в определенные сроки с определенным процентом. Акции, в свою очередь, представляют собой долю в собственности компании, и их владельцы могут получать дивиденды в случае прибыли компании.',
                'Одним из главных преимуществ облигаций является более низкий уровень риска, чем у акций. Также облигации предоставляют фиксированный доход, тогда как доходность акций зависит от успеха компании и может быть нестабильной. Однако, потенциальная доходность акций может быть выше, чем доходность облигаций.',
                'При выборе между облигациями и акциями, инвестор должен обращать внимание на несколько факторов, включая свои финансовые цели, уровень риска, диверсификацию портфеля, стоимость инструментов и уровень доходности. Кроме того, инвестор должен учитывать макроэкономические факторы, такие как инфляция и процентные ставки.'
            ],
        'На что обратить внимание':
            [
                'Кредитный рейтинг эмитента. Это оценка надежности заемщика и его способности вернуть долговые обязательства. Чем выше рейтинг, тем меньше вероятность дефолта (невозврата долга), но и доходность может быть ниже. Низкий рейтинг может означать более высокий риск, но и более высокую доходность.',
                'Ставку купона. Это процентная ставка, которую инвестор получает за пользование своими деньгами. Чем выше купон, тем выше доходность, но и риск может быть выше.',
                'Срок облигации. Чем дольше срок облигации, тем выше риск и тем выше доходность. Если же вы предпочитаете более консервативный подход, то лучше выбрать облигации с более коротким сроком.',
                'Ликвидность облигации. Облигации могут быть ликвидными (быстро обмениваются на деньги) или неликвидными (труднее продать). Облигации с низкой ликвидностью могут быть более выгодными, но и риск может быть выше.',
                'Валюта облигации. Облигации могут быть выпущены в различных валютах. Необходимо учитывать валютный риск и факторы, которые могут повлиять на курс валюты.',
                'Политическая и экономическая ситуация в стране, где выпущена облигация, также могут повлиять на ее стоимость и доходность.'
            ],
        'Ключевые параметры':
            [
                'Одним из основных параметров облигаций является купонная ставка, которая представляет собой процент, выплачиваемый инвестору за пользование его деньгами.',
                'Также важным параметром является срок облигации, который определяет, через какой период времени произойдет ее погашение и инвестор получит обратно вложенные средства.'
            ],
    }

    resume_dict = {
        'Резюме':
            [
                'Облигации являются одним из наиболее распространенных инструментов инвестирования на рынке ценных бумаг. Как мы выяснили, облигации - это долговые ценные бумаги, которые выпускаются компаниями, банками и государствами для привлечения дополнительных средств. Облигации отличаются от акций тем, что не дают права на участие в управлении эмитентом, но обладают фиксированным доходом.',
                'При выборе облигаций необходимо обращать внимание на несколько важных параметров, таких как кредитный рейтинг эмитента, купонную ставку, срок погашения, а также наличие ликвидности на рынке. Сравнение облигаций с вкладами показывает, что облигации могут быть более выгодными для инвесторов, которые ищут стабильный доход и готовы вложить деньги на более длительный период времени. В то же время, вклады могут быть более привлекательными для тех, кто ищет максимальную ликвидность и готов рисковать меньше.',
                'В целом, облигации - это инструмент инвестирования, который может быть полезен для тех, кто ищет стабильный доход и не готов рисковать на фондовом рынке. Однако, как и при любом инвестировании, необходимо тщательно изучать рынок и выбирать облигации, соответствующие вашим целям и рисковым предпочтениям.'
            ]
    }

    # КОСТЫЛЬ (автоматическая нумерация списка)
    cnt = s = 0
    key = 'На что обратить внимание'
    for row in text_dict[key]:
        cnt += 1
        new_row = f'{cnt}. {row}'
        text_dict[key][s] = new_row
        s += 1

    return render_template(
        'what-are-bonds.html',
        name_app=NAME_APP,
        header_link='Войти',
        header_redirect='/login',
        title=what_are_bonds_text.keys(),
        what_are_bonds_text=what_are_bonds_text,
        texts=text_dict,
        resume=resume_dict
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

    return render_template(
        'bonds.html',
        name_app=NAME_APP,
        title='Облигации',
        header_link='Войти',
        header_redirect='/login',
        bond_array=bond.return_saved_bonds_for_display(),
        summary_price=bond.return_summary_price_for_display(),
        profitability_per_year=bond.profitability_per_year_for_display(),
        bonds_frame=bonds_controller.bonds_frame()
    )


@app.route('/assets/bonds/analytics')
def anal_bonds():
    bond = bonds.SummaryAnalysisBondsOfIndicators()
    bonds_controller = bonds.BondsController()

    return render_template(
        'bonds-analytics.html',
        title='Анал',
        bond_ticker='RU000A'
    )


@app.route('/assets/bonds/delete/<int:bond_id>')
def delete_bond(bond_id):
    print('Запущено: delete_bond')
    try:
        RequestProcessingInDataBase.delete_record(bond_id)
        return redirect("/assets/bonds")
    except Exception as e:
        split_error = "Ошибка при удалении: Не удалось удалить облигацию из базы данных."
        return render_template(
            'error.html',
            error_code=split_error[0],
            error_text=split_error[1]
        )


@app.route('/assets/bonds/about/<string:ticker>')
def about_bond(ticker):
    bonds_db = db_manager.DataBaseManager()

    # Поиск данных об облигации из БД
    found_bond = bonds_db.select_row_from_table(bonds.BONDS_DATA_BASE, bonds.BONDS_TABLE_NAME, '*', 'ticker', ticker)

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
    title = 'О сервисе'
    text_about = '"FinanceFlow" - это мощный инструмент для управления вашими финансами. ' \
                 'С помощью этого приложения вы можете легко рассчитать доходность вклада и облигаций, ' \
                 'а также следить за своими финансовыми потоками. Вы можете добавлять свои доходы и расходы ' \
                 'в приложение и получать детальные отчеты о своей финансовой активности. FinanceFlow поможет' \
                 ' вам оставаться в курсе вашей финансовой ситуации и позволит вам принимать более обоснованные' \
                 ' финансовые решения.'
    return render_template(
        'about.html',
        name_app=NAME_APP,
        header_link='Войти',
        header_redirect='/login',
        title=title,
        text_about=text_about
    )


@app.route('/licence')
def licence():
    return render_template(
        'licence.html',
        name_app=NAME_APP,
        title='Лицензия',
        header_link='Войти',
        header_redirect='/login'
    )


@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(error):
    split_error = str(error).split(':')
    return render_template(
        'error.html',
        name_app=NAME_APP,
        title='Ошибка сервера',
        header_link='Войти',
        header_redirect='/login',
        error_code=split_error[0],
        error_text=split_error[1]
    )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
