from openpyxl import load_workbook
import os
from flask import Flask, render_template, request
from markupsafe import escape
from DBcm import UseDatabase

app = Flask(__name__)

app.config['dbconfig'] = {'host': '127.0.0.1',
            'user': 'engineer.sever', 'password': '1234567',
            'database': 'investrent'}

@app.route('/')
def log_in() ->'html':
    return render_template('index.html', the_title='invest-rent')

# def write_db (i, key_, dict_) -> None:
#     with UseDatabase(dbconfig) as cursor:
#         _SQL = """insert into metersdud(num, number, coefficient, place, tenant, enviroment) 
#         values (%s, %s, %s, %s, %s, %s)"""
#         cursor.execute(_SQL, (i, key_, dict_['coefficient'], dict_['place'], dict_['tenant'], dict_['enviroment']))
if __name__ == "__main__":
    app.run(debug=True)