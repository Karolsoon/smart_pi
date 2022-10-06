import psycopg2

import credentials

USER = credentials.USER
PASSWORD = credentials.PASSWORD
HOST = credentials.HOST
PORT = credentials.PORT
DBNAME = 'smart_home'


class pgDriver():
    dbname = DBNAME

    def __init__(self):
        self.connection = None
        self.cursor = None
        #self.dbname = self.dbname

    def __enter__(self):
        self.connection = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=self.dbname,
            user=USER,
            password=PASSWORD
        )
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exception, value, trace):
        if exception or value:
            self.rollback_transaction()
            print(f'DB Error: {exception}, {value}, {trace}')
        else:
            self.commit_transaction()

    def rollback_transaction(self):
        self.connection.rollback()
        self.cursor.close()
        self.connection.close()

    def commit_transaction(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
