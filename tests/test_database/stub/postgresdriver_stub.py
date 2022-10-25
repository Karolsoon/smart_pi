from database.postgresdriver import pgDriver


class pgDriverStub(pgDriver):

    def __init__(self, credentials: dict):
        super().__init__()
        self.HOST = credentials['host']
        self.PORT = credentials['port']
        self.USER = credentials['user']
        self.PASSWORD = credentials['password']
        self.DBNAME = credentials['dbname']
