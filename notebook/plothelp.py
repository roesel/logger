from tinydb import TinyDB, where, Query
import os
from datetime import datetime


def load_data(date):
    data = raw_data(date)
    x, y = [], []
    for row in data:
        x.append(datetime.fromtimestamp(row['stamp'] / 1e3))
        y.append(row['temperature'])
    return x, y


def raw_data(date):
    db_folder = os.path.join("C:\\", "Data\\")
    strdate = date.strftime("%y-%m-%d")
    db = TinyDB(db_folder + strdate + ".json", default_table='arduino')
    table = db.table('arduino')
    data = table.all()
    return data
