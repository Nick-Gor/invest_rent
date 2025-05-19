import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_session import Session
from markupsafe import escape
from DBcm import UseDatabase
import json
from datetime import date
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'  # You can also use 'redis' or 'mongodb'
app.config['SECRET_KEY'] = 'your_secret_key'

Session(app)

app.config['dbconfig'] = {'host': '127.0.0.1',
            'user': 'engineer.sever', 'password': '1234567',
            'database': 'investrent'}

selected_month = date.today().month
selected_year = date.today().year
date_ = date.today()
month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октрябрь", "Ноябрь", "Декабрь"]

def read_db(
    table_name: str,
    columns: list[str] = ["*"],
    condition: str = None,
    condition_params: tuple = None,
    fetch_all: bool = False
) -> list:
    """
    Universal function to read data from MySQL database

    Args:
        table_name: Name of the table to query
        columns: List of columns to select (default selects all)
        condition: WHERE clause conditions (without 'WHERE')
        condition_params: Parameters for the condition (prevents SQL injection)
        fetch_all: True to fetch all rows, False for single row

    Returns:
        List of rows (as dictionaries) or single row if fetch_all=False
    """
    with UseDatabase(app.config['dbconfig']) as cursor:
        # Validate table name
        if not table_name.replace('_', '').isalnum():
            raise ValueError("Invalid table name")

        # Build query
        columns_str = ', '.join(columns) if columns != ["*"] else "*"
        query = f"SELECT {columns_str} FROM `{table_name}`"

        if condition:
            query += f" WHERE {condition}"

        # Execute query (with or without params)
        if condition and condition_params:
            cursor.execute(query, condition_params)
        else:
            cursor.execute(query)

        # Convert rows to dictionaries
        cursor.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))

        # Fetch results (and ensure all are consumed)
        if fetch_all:
            results = cursor.fetchall()
        else:
            results = cursor.fetchone()

        # Explicitly consume any remaining unread results
        if cursor.with_rows:
            cursor.fetchall()  # Clear buffer

        return results

# функция исправления данных в таблицах

def update_db(
    table_name: str,
    data: dict,
    condition: str,
    condition_params: tuple,
    fetch_all: bool = False
) -> str:
    """
    Universal function to udate data from MySQL database

    Args:
        table_name: Name of the table to query
        data: dictionary of data to write in the table
        condition: WHERE clause conditions (without 'WHERE')
        condition_params: Parameters for the condition (prevents SQL injection)
        fetch_all: True to fetch all rows, False for single row

    Returns:
        Message
    """
    with UseDatabase(app.config['dbconfig']) as cursor:
        # Validate table name
        if not table_name.replace('_', '').isalnum():
            raise ValueError("Invalid table name")

        # Build query

        data_str = ' '.join(k+"="+"'"+v+"'," for k,v in data.items())[0:-1]
        query = f"UPDATE `{table_name}` SET {data_str}"

        if condition:
            query += f" WHERE {condition}"

        # Execute query (with or without params)
        if condition and condition_params:
            cursor.execute(query, condition_params)
        else:
            raise ValueError("Не заданы условия для выбора ячейки")

        # Fetch results (and ensure all are consumed)
        if fetch_all:
            results = cursor.fetchall()
        else:
            results = cursor.fetchone()

        # Explicitly consume any remaining unread results
        if cursor.with_rows:
            cursor.fetchall()  # Clear buffer
        message = "Данные успешно записаны"
        return message

def get_last_num(table_name:str):
    with UseDatabase(app.config['dbconfig']) as cursor:
        # First validate the table name to prevent SQL injection
        if not table_name.isidentifier() or not table_name.replace('_', '').isalnum():
            raise ValueError("Invalid table name")
        _SQL = f"SELECT MAX(num) FROM `{table_name}`"  # Backticks for safety
        cursor.execute(_SQL)
        contents = cursor.fetchone()  # Use fetchone() since we're getting a single value
        return int(contents[0]) if contents else None

@app.route('/', methods=['POST', 'GET'])
def log_in() ->'html':
    return render_template('index.html', the_title='invest-rent')


@app.route('/insertdud')
def insertdud():
    contents = []
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select number, place, enviroment from metersdud"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()
        data_dud=dict()
    for item in contents:
        data_dud[item[0]] = "".join(item[1:])
    session['data_dud'] = data_dud
    return render_template('insertdud.html')

@app.route('/insertdud/search')
def searchdud():
    data_dud = session.get('data_dud')
    query = request.args.get('query', '').lower()
    results = {k: v for k, v in data_dud.items() if query in k.lower()}
    return jsonify(results)

@app.route('/save_selection', methods=['POST'])
def save_selection():
    selected_data = request.json
    number = selected_data['key']
    place = selected_data['value']
    session['place'] = place
    session['number'] = number
    return jsonify({"status": "success"})

@app.route('/insertdud/search/check', methods=["GET", "POST"])
def check_dud():
    global selected_year, selected_month
    number = session.get('number')
    place = session.get('place')
    month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                  "Июль", "Август", "Сентябрь", "Октрябрь", "Ноябрь", "Декабрь"]
    date_  = date.today()
    # selected_month = date.today().month
    # selected_year = date.today().year
    notification = ''
    contents = dict()
    if request.method == 'POST':
        selected_month = int(request.form.get('month', selected_month))
        selected_year = int(request.form.get('year', selected_year))
        session['selected_year'] = selected_year
        if selected_month !=1:
            prev_month = month_names[selected_month-2]
            year_for_prev_month = selected_year
        else:
            prev_month = month_names[11]
            year_for_prev_month = selected_year - 1
        condition = "number = %s AND month = %s AND year = %s"
        params = (number, prev_month, year_for_prev_month)
        contents = read_db(
            table_name="valuesdud",
            columns=["debit", "value"],
            condition=condition,
            condition_params=params
        )
        debit_prev = contents[0]
        value_prev = contents[1]
        condition = "number = %s AND month = %s AND year = %s"
        params = (number, month_names[selected_month-1], selected_year)
        result = read_db(
            table_name="valuesdud",
            columns=["number", "month", "year", "value"],
            condition=condition,
            condition_params=params
        )

        condition = "number = %s"
        params = (number,)
        coefficient = int(read_db(
            table_name="metersdud",
            columns=["coefficient"],
            condition=condition,
            condition_params=params            
        )[0])
        if result:
            notification = f"В базе данных уже есть показания по счетчику №{result[0]} за {result[1]} {result[2]} - {result[3]}"
        return render_template('check.html', notification=notification, number=number, place=place, date=date_,
                               selected_month=selected_month, selected_year=selected_year, month_names=month_names,
                               debit_prev=debit_prev, value_prev=value_prev, coefficient=coefficient)
    return render_template('check.html', number=number, place=place, date=date_, selected_month=selected_month, selected_year=selected_year)

@app.route('/insertdud/write_value', methods=["POST"])
def write_value():
    global date_
    num = get_last_num('valuesdud')+1
    number = session.get('number')
    value_for_writing = request.json
    value = value_for_writing['value']
    debit = value_for_writing['debit']
    month = value_for_writing['month']
    year_ = session.get('selected_year')
    # year_ = int(value_for_writing['year'])
    # condition = "number = %s"
    # params = (str(number),)
    # enviroment = read_db(
    #     table_name="metersdud",
    #     columns=["enviroment"],
    #     condition="number = %s",
    #     condition_params=(str(number),),  # Note the comma for single-element tuple
    #     fetch_all=False
    # )
    _SQL = f"SELECT enviroment from `metersdud` where number='{number}';"
    print(_SQL)
    with UseDatabase(app.config['dbconfig']) as cursor:
        cursor.execute(_SQL)
        enviroment = cursor.fetchone()[0]

    # enviroment = 'water'
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into valuesdud(num, number, enviroment, month, year, date, debit, value)
        values (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (num, number, enviroment, month, year_, date_, debit, value))
    return jsonify({'status': 'success','message': 'Reading saved successfully',
                    'redirect': '/insertdud'})

@app.route('/insertverkh')
def insertverkh():
    contents = []
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select number_v, place, enviroment from metersverkh"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()
        data_verkh=dict()
    for item in contents:
        data_verkh[item[0]] = "".join(item[1:])
    session['data_verkh'] = data_verkh
    return render_template('insertverkh.html')

@app.route('/insertverkh/search')
def searchverkh():
    data_verkh = session.get('data_verkh')
    query = request.args.get('query', '').lower()
    results = {k: v for k, v in data_verkh.items() if query in k.lower()}
    return jsonify(results)

@app.route('/insertverkh/search/check_verkh', methods=["GET", "POST"])
def check_verkh():
    global selected_year, selected_month
    number = session.get('number')
    place = session.get('place')
    month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                  "Июль", "Август", "Сентябрь", "Октрябрь", "Ноябрь", "Декабрь"]
    date_  = date.today()
    # selected_month = date.today().month
    # selected_year = date.today().year
    notification = ''
    contents = dict()
    if request.method == 'POST':
        selected_month = int(request.form.get('month', selected_month))
        selected_year = int(request.form.get('year', selected_year))
        session['selected_year'] = selected_year
        if selected_month !=1:
            prev_month = month_names[selected_month-2]
            year_for_prev_month = selected_year
        else:
            prev_month = month_names[11]
            year_for_prev_month = selected_year - 1
        condition = "number_v = %s AND month = %s AND year = %s"
        params = (number, prev_month, year_for_prev_month)
        contents = read_db(
            table_name="valuesverkh",
            columns=["debit", "value"],
            condition=condition,
            condition_params=params
        )
        debit_prev = contents[0]
        value_prev = contents[1]
        condition = "number_v = %s AND month = %s AND year = %s"
        params = (number, month_names[selected_month-1], selected_year)
        result = read_db(
            table_name="valuesverkh",
            columns=["number_v", "month", "year", "value"],
            condition=condition,
            condition_params=params
        )
        condition = "number_v = %s"
        params = (number,)
        coefficient = int(read_db(
            table_name="metersverkh",
            columns=["coefficient"],
            condition=condition,
            condition_params=params            
        )[0])

        if result:
            notification = f"В базе данных уже есть показания по счетчику №{result[0]} за {result[1]} {result[2]} - {result[3]}"
        return render_template('check_verkh.html', notification=notification, number=number, place=place, date=date_,
                               selected_month=selected_month, selected_year=selected_year, month_names=month_names,
                               debit_prev=debit_prev, value_prev=value_prev, coefficient=coefficient)
    return render_template('check_verkh.html', number=number, place=place, date=date_, selected_month=selected_month, selected_year=selected_year)

@app.route('/insertverkh/write_value', methods=["POST"])
def write_value_verkh():
    global date_
    num = get_last_num('valuesverkh')+1
    number = session.get('number')
    value_for_writing = request.json
    value = value_for_writing['value']
    debit = value_for_writing['debit']
    month = value_for_writing['month']
    year_ = session.get('selected_year')
    # year_ = int(value_for_writing['year'])
    _SQL = f"SELECT enviroment from `metersverkh` where number_v='{number}';"
    with UseDatabase(app.config['dbconfig']) as cursor:
        cursor.execute(_SQL)
        enviroment = cursor.fetchone()[0]
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into valuesverkh(num, number_v, enviroment, month, year, date, debit, value)
        values (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (num, number, enviroment, month, year_, date_, debit, value))
    return jsonify({'status': 'success','message': 'Reading saved successfully',
                    'redirect': '/insertverkh'})

# вывод оставшихся счетчиков

@app.route('/remain', methods=["GET", "POST"])
def remaindud():
    global selected_month, selected_year, month_names
    if request.method == 'POST':
        table_name = request.form.get('optobject')
        submit = True
        if table_name== 'valuesdud':
            table_name_meters = 'metersdud'
            columns_meters=['number','place', 'enviroment']
        else:
            table_name_meters = 'metersverkh'
            columns_meters=['number_v', 'place', 'enviroment']
        all_meters = read_db(
            table_name=table_name_meters,
            columns=columns_meters,
            fetch_all=True
        )
        if table_name== 'valuesdud':
            columns=['number']
        else:
            columns=['number_v']
        selected_month_req = month_names[int(request.form.get('month'))-1]
        selected_year_req = request.form.get('year')
        condition = "month = %s AND year = %s"
        params = (selected_month_req, selected_year_req)
        result = read_db(
            table_name=table_name,
            columns=columns,
            condition=condition,
            condition_params=params,
            fetch_all=True
        )
        readed_meters=[]
        for r in result:
            for l in r:
                readed_meters.append(l)

        remain_meters=[]
        for item in all_meters:
            if item[0] not in readed_meters:
                remain_meters.append(item)
        remain = len(remain_meters)
        return render_template('remain.html', remain_meters=remain_meters, submit=submit, remain=remain,
                               selected_month=selected_month, selected_year=selected_year)
    return render_template('remain.html', selected_month=selected_month, selected_year=selected_year)


@app.route('/report', methods=["GET", "POST"])
def report():
    global selected_year, selected_month
    month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    if request.method == 'POST':
        table_name = request.form.get('optobject')
        submit = True
        selected_month_req = month_names[int(request.form.get('month'))-1]
        selected_year_req = request.form.get('year')
        condition = "month = %s AND year = %s"
        params = (selected_month_req, selected_year_req)

        if table_name == 'valuesdud':
            columns=['number', 'enviroment', 'year', 'month', 'date', 'debit', 'value']
        else:
            columns=['number_v', 'enviroment', 'year', 'month', 'date', 'debit', 'value']

        result = read_db(
            table_name=table_name,
            columns=columns,
            condition=condition,
            condition_params=params,
            fetch_all=True
        )

        if table_name == 'valuesdud':
            table_name_t = 'metersdud'
            columns_t = ['number', 'place', 'tenant']
        else:
            table_name_t = 'metersverkh'
            columns_t = ['number_v', 'place', 'tenant']

        tenants = read_db(
            table_name=table_name_t,
            columns=columns_t,
            fetch_all=True
        )

        dic_tenants = {item[0]: item[1:] for item in tenants}

        report_list = []
        for row in result:
            place, tenant = dic_tenants.get(row[0], ('', ''))
            report_list.append([
                row[3], # месяц
                row[2], # год
                row[4], # дата
                row[0], # номер счетчика
                place,  # место установки
                tenant, # арендатор
                row[1], # среда установки
                row[5], # расход
                row[6]  # показания
            ])
        session['report_data'] = report_list
        session['selected_month_req'] = selected_month_req
        session['selected_year_req'] = selected_year_req
        session['object'] = table_name[6:]

        return render_template('report.html',
                             submit=submit,
                             result=report_list,
                             selected_month=selected_month,
                             selected_year=selected_year,
                             selected_month_req=selected_month_req,
                             selected_year_req=selected_year_req)

    return render_template('report.html', selected_month=selected_month, selected_year=selected_year)

@app.route('/export_excel')
def export_excel():
    report_data = session.get('report_data', [])
    month = session.get('selected_month_req', '')
    year = session.get('selected_year_req', '')
    object = session.get('object')

    if not report_data:
        return "No data to export", 400

    df = pd.DataFrame(report_data, columns=[
        'Месяц', 'Год', 'Дата', 'Номер счетчика', 'Место', 'Арендатор', 'Среда',
         'Расход', 'Показания'
    ])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Отчет', index=False)
    output.seek(0)

    filename = f"отчет_{object}_{month}_{year}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/process', methods=['POST', 'GET'])
def process():
    dropdown_source = request.form.get('dropdown_source')
    table_name = request.form.get('dropdown_value')
    contents = []
    if table_name=='metersdud':
        columns=['number', 'place', 'tenant']
    else:
        columns=['number_v', 'place', 'tenant']
    contents = read_db(table_name,
                       columns,
                       fetch_all=True)
    data_numbers=dict()
    for item in contents:
        data_numbers[item[0]] = "".join(item[1:])
    session['data_dud'] = data_numbers
    session['table_name'] = table_name
    session['dropdown_source'] = dropdown_source
    return render_template('search_number_update.html', dropdown_source=dropdown_source, 
                           table_name=table_name)


@app.route('/fill_card', methods = ['POST', 'GET'])
def fill():
    global selected_month, selected_year, month_names
    update_type = request.form.get('table')
    number = session.get('number')
    table_name = session.get('table_name')
    session['update_type'] = update_type
    if update_type=='meters':
        if table_name == 'metersdud':
            condition = "number=%s"
        else:
            condition = "number_v=%s"
        
        row = read_db(table_name=table_name,
                      condition=condition,
                      condition_params=(number,),
                      fetch_all=False)
        num = row[0]
        coefficient = row[2]
        place = row[3]
        tenant = row[4]
        enviroment = row[5]
        session['num'] = num
        return render_template('meters_card_fill.html', number=number,
                               coefficient=coefficient, place=place, tenant=tenant, 
                               enviroment=enviroment)

    return render_template('values_card_fill.html', selected_month=selected_month, selected_year=selected_year)


@app.route('/select_month_year', methods=['POST'])
def select_month_year():
    global selected_month, selected_year, month_names
    number = session.get('number')
    table_name = session.get('table_name')
    
    selected_month_req = month_names[int(request.form.get('month'))-1]
    selected_year_req = request.form.get('year')
    
    columns_t = ['num', 'debit', 'value']
    if table_name == 'metersdud':
        table_name_t = 'valuesdud'
        condition = "number=%s AND month = %s AND year = %s"
    else:
        table_name_t = 'valuesverkh'
        condition = "number_v=%s AND month = %s AND year = %s"

    readings = read_db(
        table_name=table_name_t,
        columns=columns_t,
        condition=condition,
        condition_params=(number, selected_month_req, selected_year_req),
        fetch_all=False
    )
    if readings:
        num = readings[0]
        debit = readings[1]
        value = readings[2]  
        session['num'] = num
        session['selected_month']=selected_month_req
        session['selected_year']=selected_year_req
        return render_template('values_card_fill.html', 
                             number=number, 
                             selected_month_req=selected_month_req,
                             selected_year_req=selected_year_req, 
                             debit=debit, 
                             value=value, 
                             submit=True)
    
    # If no readings found, show empty form
    return render_template('values_card_fill.html',
                         number=number,
                         selected_month_req=selected_month_req,
                         selected_year_req=selected_year_req,
                         submit=True)

@app.route('/written_card',  methods=['POST', 'GET'])
def write_card():
    update_type= session.get('update_type')
    num = session.get('num')
    table_name = session.get('table_name')
    number = session.get('number')

    if update_type == 'meters':
        number = str(request.form.get('number'))
        coefficient = str(request.form.get('coefficient'))
        place = request.form.get('place')
        tenant = request.form.get('tenant')
        enviroment = request.form.get('enviroment')
        if table_name == 'metersdud':
            data = {'number': number, 'coefficient': coefficient, 'place': place, 'tenant': tenant, 'enviroment': enviroment}
        else:
            data = {'number_v': number, 'coefficient': coefficient, 'place': place, 'tenant': tenant, 'enviroment': enviroment}
        message = update_db(
            table_name=table_name,
            data = data,
            condition='num=%s',
            condition_params=(num,),
            fetch_all=False
        )
        return render_template('written_card.html', update_type=update_type, num=num, number=number, coefficient=coefficient,
                           place=place, tenant=tenant, enviroment=enviroment, message=message)
    else:
        selected_year = session.get('selected_year')
        selected_month = session.get('selected_month')
        debit = request.form.get('debit')
        value = request.form.get('value')
        data = {'debit': debit, 'value': value}
        if table_name == 'metersdud':
            table_name_t='valuesdud'
        else:
            table_name_t = 'valuesverkh'
        message = update_db(
            table_name=table_name_t,
            data=data,
            condition='num=%s',
            condition_params=(num, ),
            fetch_all=False
        )
        return render_template('written_card.html', update_type=update_type, num=num,
                               number=number, debit=debit, value=value, selected_month=selected_month,
                               selected_year=selected_year, message=message)

if __name__ == "__main__":
    app.run(debug=True)

# сделать неактивной кнопку ввода не подтверждены месяц и год
# сделать выделение красным для отрицательных значений расхода
# разобраться с сеткой при отображении на смартфоне
# добавить ввод координат
# написать функции для записи показания для первого верхнего
# написать функцию для вывода оставшихся счетчиков
# написать функцию для вывода ввденных покзаний в excel
# добавить обработку ошибок для обращения к отсутвтвующим данным в БД
# попробовать как будет работать при одновременном вводе показаний по верхнему и дудина
# сделать функцию записи данных универсальной путем передачи имени таблицы. Можно передавать его на странцу и брать потом при помщи JS, а лучше спросить deepseek как передать непосредственнов в JS
