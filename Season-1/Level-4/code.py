'''
Please note:

The first file that you should run in this level is tests.py for database creation, with all tests passing.
Remember that running the hack.py will change the state of the database, causing some tests inside tests.py
to fail.

If you like to return to the initial state of the database, please delete the database (level-4.db) and run
the tests.py again to recreate it.
'''

import sqlite3
import os
import re
import pathlib
from flask import Flask, request

### Unrelated to the exercise -- Starts here -- Please ignore
app = Flask(__name__)
@app.route("/")
def source():
    DB_CRUD_ops().get_stock_info(request.args["input"])
    DB_CRUD_ops().get_stock_price(request.args["input"])
    DB_CRUD_ops().update_stock_price(request.args["input"])
    DB_CRUD_ops().exec_multi_query(request.args["input"])
    DB_CRUD_ops().exec_user_script(request.args["input"])
### Unrelated to the exercise -- Ends here -- Please ignore

class Connect(object):

    # helper function creating database with the connection
    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
        except sqlite3.Error as e:
            print(f"ERROR: {e}")
        return connection

class Create(object):

    def __init__(self):
        con = Connect()
        try:
            # creates a dummy database inside the folder of this challenge
            path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(path, 'level-4.db')
            db_con = con.create_connection(db_path)
            cur = db_con.cursor()

            # checks if tables already exist, which will happen when re-running code
            table_fetch = cur.execute(
                '''
                SELECT name
                FROM sqlite_master
                WHERE type='table'AND name='stocks';
                ''').fetchall()

            # if tables do not exist, create them and insert dummy data
            if table_fetch == []:
                cur.execute(
                    '''
                    CREATE TABLE stocks
                    (date text, symbol text, price real)
                    ''')

                # inserts dummy data to the 'stocks' table, representing average price on date
                cur.execute(
                    "INSERT INTO stocks VALUES ('2022-01-06', 'MSFT', 300.00)")
                db_con.commit()

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            db_con.close()

SYMBOL_RE = re.compile(r'[A-Za-z0-9.]{1,10}')

def sanitize_symbol(stock_symbol):
    if not isinstance(stock_symbol, str):
        raise Exception("ERROR: stock symbol must be a string")
    match = SYMBOL_RE.match(stock_symbol)
    if not match:
        raise Exception("ERROR: invalid stock symbol")
    return match.group(0)

def db_path():
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, 'level-4.db')

def read_only_connection():
    uri = pathlib.Path(db_path()).as_uri() + '?mode=ro'
    return sqlite3.connect(uri, uri=True)

ALLOWED_QUERIES = [
    (re.compile(r"SELECT\s+price\s+FROM\s+stocks\s+WHERE\s+symbol\s*=\s*'([A-Za-z0-9.]{1,10})'", re.I),
     "SELECT price FROM stocks WHERE symbol = ?"),
    (re.compile(r"SELECT\s+\*\s+FROM\s+stocks\s+WHERE\s+symbol\s*=\s*'([A-Za-z0-9.]{1,10})'", re.I),
     "SELECT * FROM stocks WHERE symbol = ?"),
]

def run_allowed_query(cur, query):
    for pattern, statement in ALLOWED_QUERIES:
        match = pattern.fullmatch(query.strip())
        if match:
            cur.execute(statement, (match.group(1),))
            return cur.fetchall()
    raise sqlite3.Error("query is not allowed")

class DB_CRUD_ops(object):

    # retrieves all info about a stock symbol from the stocks table
    # Example: get_stock_info('MSFT') will result into executing
    # SELECT * FROM stocks WHERE symbol = 'MSFT'
    def get_stock_info(self, stock_symbol):
        db = Create()
        con = Connect()
        db_con = None
        try:
            db_con = con.create_connection(db_path())
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] get_stock_info\n"
            query = "SELECT * FROM stocks WHERE symbol = '{0}'".format(stock_symbol)
            res += "[QUERY] " + query + "\n"

            restricted_chars = ";%&^!#-"
            has_restricted_char = any([char in query for char in restricted_chars])
            correct_number_of_single_quotes = query.count("'") == 2

            if has_restricted_char or not correct_number_of_single_quotes:
                res += "CONFIRM THAT THE ABOVE QUERY IS NOT MALICIOUS TO EXECUTE"
            else:
                cur.execute("SELECT * FROM stocks WHERE symbol = ?", (stock_symbol,))
                for result in cur.fetchall():
                    res += "[RESULT] " + str(result)
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()

    # retrieves the price of a stock symbol from the stocks table
    # Example: get_stock_price('MSFT') will result into executing
    # SELECT price FROM stocks WHERE symbol = 'MSFT'
    def get_stock_price(self, stock_symbol):
        db = Create()
        con = Connect()
        db_con = None
        try:
            symbol = sanitize_symbol(stock_symbol)
            db_con = con.create_connection(db_path())
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] get_stock_price\n"
            res += "[QUERY] SELECT price FROM stocks WHERE symbol = '" + symbol + "'\n"
            cur.execute("SELECT price FROM stocks WHERE symbol = ?", (symbol,))
            for result in cur.fetchall():
                res += "[RESULT] " + str(result) + "\n"
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()

    # updates stock price
    def update_stock_price(self, stock_symbol, price):
        db = Create()
        con = Connect()
        db_con = None
        try:
            if not isinstance(price, float):
                raise Exception("ERROR: stock price provided is not a float")
            symbol = sanitize_symbol(stock_symbol)

            db_con = con.create_connection(db_path())
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] update_stock_price\n"
            res += "[QUERY] UPDATE stocks SET price = '%d' WHERE symbol = '%s'\n" % (price, symbol)
            cur.execute("UPDATE stocks SET price = ? WHERE symbol = ?", (price, symbol))
            db_con.commit()
            for result in cur.fetchall():
                res += "[RESULT] " + str(result)
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()

    # executes multiple read-only queries
    # Example: SELECT price FROM stocks WHERE symbol = 'MSFT';
    #          SELECT * FROM stocks WHERE symbol = 'MSFT'
    def exec_multi_query(self, query):
        db = Create()
        db_con = None
        try:
            db_con = read_only_connection()
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] exec_multi_query\n"
            for query in filter(None, query.split(';')):
                res += "[QUERY]" + query + "\n"
                for result in run_allowed_query(cur, query):
                    res += "[RESULT] " + str(result) + " "
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()

    # executes a single read-only query supplied by the user
    # Example: SELECT price FROM stocks WHERE symbol = 'MSFT'
    def exec_user_script(self, query):
        db = Create()
        db_con = None
        try:
            db_con = read_only_connection()
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] exec_user_script\n"
            res += "[QUERY] " + query + "\n"
            for result in run_allowed_query(cur, query):
                res += "[RESULT] " + str(result)
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()
