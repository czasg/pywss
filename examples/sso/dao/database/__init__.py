# coding: utf-8
import os
import loggus
import sqlite3
import sqlalchemy

from sqlalchemy import create_engine
engine = create_engine('sqlite:///foo.db')
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sso.db")
DB = sqlite3.connect(DB_FILE, isolation_level=None)
DB.row_factory = dict_factory


def execute(sql, commit=False):
    cursor = DB.cursor()
    cursor.execute(sql)
    if commit:
        DB.commit()
    result = cursor.fetchall()
    cursor.close()
    return result


class UserMetaClass(type):

    def __new__(cls, name, base, attr):
        if base:
            loggus.withFields({"base": base}).panic("不支持继承")

        def rowSQL(key: str, keyType):
            if not key:
                loggus.panic("不能定义空字段")
            keys = key[0].lower() + key[1:]
            for k in keys:
                if k.isupper():
                    keys = keys.replace(k, f"_{k.lower()}", 1)
            if keys == "id":
                return "id INTEGER PRIMARY KEY"
            if keyType == int:
                return f"{keys} bigint(64) NULL"
            elif keyType == str:
                return f"{keys} varchar(255) NULL"

        RowSQL = ",\n".join([rowSQL(key, keyType) for key, keyType in attr["__annotations__"].items()])
        SQL = f"""
CREATE TABLE IF NOT EXISTS `{name.lower()}` (
{RowSQL}
);
""".strip()
        with loggus.withTraceback():
            execute(SQL)
        return type.__new__(cls, name, base, attr)


class User(metaclass=UserMetaClass):
    Id: int
    Name: str
    Password: str
    Email: str
    CreateAt: int
    UpdateAt: int
    LoginAt: int

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            k = "".join([i[0].upper() + i[1:] for i in k.split("_")])
            setattr(self, k, v)
