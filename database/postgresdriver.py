import psycopg2

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
    PORT = credentials.PORT
    DBNAME = 'smart_home'

    DEFAULT_TIMEOUT = 2
    # Can't be lower than 2 seconds acc to postgres documentation.

    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self._get_connection()
        self._get_cursor()
        return self

    def _get_connection(self):
        self.connection = psycopg2.connect(
        host=self.HOST,
        port=self.PORT,
        dbname=self.DBNAME,
        user=self.USER,
        password=self.PASSWORD,
        connect_timeout=self.DEFAULT_TIMEOUT
        )

    def _get_cursor(self):
        self.cursor = self.connection.cursor()

    def __exit__(self, exception, value, trace):
        if exception or value or trace:
            self.rollback_transaction()
            return False
        else:
            self.commit_transaction()
            return True

    def rollback_transaction(self):
        self.connection.rollback()
        self.cursor.close()
        self.connection.close()

    def commit_transaction(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
