from postgresdriver import pgDriver as pgd
from database_exceptions import NotNullViolation, ColumnDoesNotExist

DBNAME = pgd.dbname

class Query():
    def __init__(self):
        self._select = None
        self._insert = None

    @classmethod
    def execute(self, query):
        with pgd() as pgdb:
            pgdb.cursor.execute(query)
            return pgdb.cursor.fetchall()

    @classmethod
    def get_tables(cls, schema: str, table_type: str):
        query = f"""
            SELECT DISTINCT
                table_name
            FROM 
                information_schema."tables" t
            WHERE 
                lower(table_schema) = '{schema.lower()}' AND
                lower(table_type) = '{table_type.lower()}';
        """
        return cls.execute(query)

    @classmethod
    def get_columns(cls, schema: str, table: str, metadata_columns):
        query = f"""
            SELECT
                {','.join(metadata_columns)}
            FROM
                information_schema."columns" c
            WHERE
                lower(table_name) = '{table.lower()}'
        """
        return cls.execute(query)

    def create(self, data: dict):
        #self.cursor.execute(query)
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass