import psycopg2
from psycopg2 import extras

from database import credentials


class pgDriver(object):
    """
    Returns self with a connection  and cursor attribute.
    Accepts an optional credentials dict as a parameter.
    Credentials: host, port, dbname, user, password.
    """
    USER = credentials.USER
    PASSWORD = credentials.PASSWORD
    HOST = credentials.HOST
    #HOST2 = credentials.HOST2
    PORT = credentials.PORT
    DBNAME = 'smart_home'

    DEFAULT_TIMEOUT = 2
    # Can't be lower than 2 seconds acc to postgres documentation.

    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        for _ in range(2):
            try:
                self._get_connection(self.HOST)
            except Exception:
                #self._get_connection(self.HOST2)
                pass

        self._get_cursor()
        return self

    def _get_connection(self, host):
        self.connection = psycopg2.connect(
        host=host,
        port=self.PORT,
        dbname=self.DBNAME,
        user=self.USER,
        password=self.PASSWORD,
        connect_timeout=self.DEFAULT_TIMEOUT
        )

    def _get_cursor(self):
        if self.connection is None:
            raise ConnectionError('Failed to get cursor')
        self.cursor = self.connection.cursor(cursor_factory=extras.DictCursor)

    def __exit__(self, exception, value, trace):
        if  value:
            self.rollback_transaction()
            return True
        self.commit_transaction()
        return True

    def rollback_transaction(self):
        self.connection.rollback()
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def commit_transaction(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
