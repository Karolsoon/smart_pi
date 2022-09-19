from typing import Tuple, List, Dict

from consoletable import ConsoleTable as ct
from dbquery import Query
from database_exceptions import NotNullViolation


DBNAME = 'smart_home'
SCHEMA = 'home'

TABLE_TYPES = ('base table',)
COLUMN_METADATA = ('column_name', 'is_nullable', 'data_type')


class DBModel():
    def __init__(self, dbname=DBNAME):
        self._dbname = dbname
        self._schemas = dict()

    def get(self):
        if not self._schemas:
            self.build()
        return self

    def build(self):
        for key in self._schemas:
            self.schema[key].build()

    @property
    def dbname(self):
        return self._dbname

    @dbname.setter
    def dbname(self, dbname: str):
        self._dbname = dbname

    @property
    def schemas(self):
        return self._schemas
    
    @schemas.setter
    def schemas(self, name: str):
        self._schemas[name] = Schema(name)


class Schema():
    def __init__(self, name: str):
        self.name = name
        self._tables = dict()
        self.build()

    def get(self):
        if not self.tables:
            self.build()
        return self

    def build(self):
        unpacked_tables = self._unpack(self._get_table_names_from_db())
        self._add_to_self(unpacked_tables)

    def _get_table_names_from_db(self, table_types: Tuple =TABLE_TYPES):
        tables = []
        for table_type in table_types:
            tables.append(Query.get_tables(self.name, table_type))
        return tables

    def _unpack(self, tables: List[List[Tuple]]) -> list:
        table_list = []
        for table in tables[0]:
            table_list.append(*table)
        return table_list

    def _add_to_self(self, table_names):
        for table_name in table_names:    
            table = Table(table_name)
            setattr(self, table_name, table)    # To be considered
            self._tables[table_name] = table

    @property
    def tables(self):
        return self._tables

    @tables.setter
    def tables(self, name: str):
        self._tables[name] = Table(name)


class Table():
    def __init__(self, name: str):
        self.name = name
        self._columns = dict()

    def __str__(self):
        return f"Table: {str(self.name)} \nColumns: {self.columns}\n"

    def get(self):
        if not self.columns:
            self._get_columns_from_db
        return self

    def build(self):
        self._get_columns_from_db

    def _get_columns_from_db(self) -> Tuple:
        for columns in Query.get_columns(SCHEMA, self.name, COLUMN_METADATA):
            self._add_to_self(columns)

    def _add_to_self(self, columns: Tuple):
        column_metadata = dict(zip(COLUMN_METADATA, columns))
        self.columns = column_metadata

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, column_metadata: Dict):
        if column_metadata['column_name']:
            self._columns[column_metadata['column_name']] = Column(column_metadata)
        else:
            raise ValueError("'column_name' missing in column header")


class Column():
    def __init__(self, column_metadata: dict):
        self._metadata = dict()
        for key in column_metadata:
            setattr(self, key, column_metadata[key])   # To be considered
            self._metadata[key] = column_metadata[key]

    def __str__(self):
        string = '\n'
        print(self.__dict__)
        for key in self.__dict__.keys():
            string += f'{key}: {self.__dict__.get(key)}\n'
        return string

    def get(self):
        return self



#
# Workbench for ideas TBC
#

db= DBModel()



# headers = [x for x in database_model.schemas['home'].tables]
# columns = [[x for x in y.columns.keys()] for y in database_model.schemas['home'].tables.values()]
# table = ct.make_table_by_columns(headers, columns)
# print(table)
