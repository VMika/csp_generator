import sqlite3
import yaml
from sqlite3 import OperationalError
from config import ROOT_DIR


def init():
    conn = sqlite3.connect('csp.db', isolation_level=None)
    cursor = conn.cursor()
    execute_command('init.sql', cursor)
    fill_db(conn)


def execute_command(file, cursor):
    fd = open(file, 'r')
    sql_file = fd.read()
    fd.close()
    sql_commands = sql_file.split(';')

    for command in sql_commands:
        try:
            cursor.execute(command)
        except OperationalError as e:
            print("Command skipped : ", e, command, '\n')


def build_data(config_file):
    path = str(ROOT_DIR / 'src' / 'config' / config_file)
    stream = open(path)
    return yaml.safe_load(stream)


def fill_db(db):
    cursor = db.cursor()
    data = build_data('reco.yaml')
    sql = 'INSERT INTO flag_info(id, description, explanation, reco) VALUES (?,?,?,?)'

    for elem in data:
        identifier = elem
        description = data[elem]['description']
        explanation = data[elem]['explanation']
        reco = data[elem]['reco']
        print(identifier, description, explanation, reco)

        cursor.execute(sql, (identifier, description, explanation, reco))
        db.commit()


init()
