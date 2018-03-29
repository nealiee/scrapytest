import sqlite3
from scrapytest.util.setting import SQLITE_DBNAME


class DataBase(object):
    def __init__(self):
        self.conn = sqlite3.connect(SQLITE_DBNAME)
        self.cur = self.conn.cursor()

    def fetch_all(self, sql):
        res = ''
        try:
            self.cur.execute(sql)
            res = self.cur.fetchall()
        except Exception as e:
            print(e)
            res = False
        return res

    def idu(self, sql):
        flag = False
        try:
            self.cur.execute(sql)
            self.conn.commit()
            flag = True
        except Exception as e:
            print(e)
            pass
        return flag

    def close(self):
        if isinstance(self.cur, object):
            self.cur.close()
        if isinstance(self.conn, object):
            self.conn.close()
