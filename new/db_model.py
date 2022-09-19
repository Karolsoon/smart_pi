from typing import Tuple, List, Dict

from prettytable import PrettyTable
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


class Schema(DBModel):
    def __init__(self, name: str):
        self.name = name
        self._tables = dict()
        super().__init__()

    def build_schema(self):
        """
        Actually sets only the tables to preserve performance. I think.
        """
        unpacked_tables = self._unpack_tables(self._get_table_names_from_db())
        self._build_tables(unpacked_tables)

    def _get_table_names_from_db(self, table_types: Tuple =TABLE_TYPES):
        tables = []
        for table_type in table_types:
            tables.append(Query.get_tables(self.name, table_type))
        return tables

    def _unpack_tables(self, tables: List[List[Tuple]]) -> list:
        table_list = []
        for table in tables[0]:
            table_list.append(*table)
        return table_list

    def _build_tables(self, unpacked_tables):
        for table in unpacked_tables:
            self._add_table(table)

    def _add_table(self, table_name):
        table = Table(table_name)
        setattr(self, table_name, table)
        self._tables[table_name] = table

    @property
    def tables(self):
        return self._tables

    @tables.setter
    def tables(self, name: str):
        self._tables[name] = Table(name)


class Table(Schema):
    def __init__(self, name: str):
        self.name = name
        self._columns = dict()

    def __str__(self):
        return f"Table: {str(self.name)} \nColumns: {self.columns}\n"

    def get_columns_from_db(self) -> Tuple:
        for columns in Query.get_columns(SCHEMA, self.name, COLUMN_METADATA):
            self._attach_columns_to_table(columns)

    def _attach_columns_to_table(self, columns: Tuple):
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
        for key in column_metadata:
            setattr(self, key, column_metadata[key])

    def __str__(self):
        string = '\n'
        print(self.__dict__)
        for key in self.__dict__.keys():
            string += f'{key}: {self.__dict__.get(key)}\n'
        return string


#
# Workbench for ideas TBC
#

database_model = DBModel()
database_model.schemas = 'home'

database_model.schemas['home'].build_schema()
database_model.schemas['home'].home_measures.get_columns_from_db()
database_model.schemas['home'].illuminance.get_columns_from_db()

print(database_model.schemas['home'].tables)
print(database_model.schemas['home'].tables['home_measures'].columns)

second_col = [x for x in database_model.schemas['home'].tables['illuminance'].columns.keys()]
second_col.extend([' ',' '])

pt = PrettyTable()
pt.add_column('home_measures', [x for x in database_model.schemas['home'].tables['home_measures'].columns.keys()])
pt.add_column('illuminance',  second_col)
print(pt)
