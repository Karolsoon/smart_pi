from typing import Tuple, List, Dict
from collections import defaultdict as dd
import time

from consoletable import ConsoleTable
from dbquery import Query



DBNAME = 'smart_home'
SCHEMA = 'home'

TABLE_TYPES = ('base table',)
COLUMN_METADATA = ('column_name', 'is_nullable', 'data_type')
EXCLUDED_SCHEMAS = ('pg_catalog', 'information_schema', 'pg_toast')


class DBModel():
    def __init__(self, dbname=DBNAME):
        self._dbname = dbname
        self._schemas = dict()
        self.get()

    def __str__(self):
        return self._dbname

    def get(self):
        if not self._schemas:
            self.build()
        return self

    def build(self):
        self._add_to_self(self._get_schema_names_from_db())

    def _get_schema_names_from_db(self):
        return Query.get_schemas(
            self.dbname, 
            self.convert_to_string(EXCLUDED_SCHEMAS)
            )

    def _add_to_self(self, schemas: Tuple[Tuple]):
        for schema_name in schemas:
            schema_object = Schema(schema_name[0])
            self.schemas[schema_name[0]] = schema_object
            setattr(self, schema_name[0], schema_object)

    @staticmethod
    def convert_to_string(an_iterable):
        converted = ''
        for x in an_iterable:
            converted += f"'{x}',"
        return converted[:-1]

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
        self._table_objects = dict()
        self.get()

    def __str__(self):
        return self.name

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

    def _unpack(self, tables: Tuple[List[Tuple]]) -> list:
        table_list = []
        for table in tables[0]:
            table_list.append(*table)
        return table_list

    def _add_to_self(self, table_names):
        for table_name in table_names:    
            table = Table(table_name, self.name)
            setattr(self, table_name, table)    # To be considered
            self._table_objects[table_name] = table

    @property
    def tables(self):
        return self._table_objects

    @tables.setter
    def tables(self, name: str):
        self._table_objects[name] = Table(name, self.name)


class Table():
    def __init__(self, name: str, schema: str):
        self.name = name
        self._schema = schema
        self._columns = dict()
        self.get()

    def __str__(self):
        return f"Table: {str(self.name)} \nColumns: {list(self.columns.keys())}\n"

    def get(self):
        if not self.columns:
            self.build()
        return self

    def build(self):
        self._get_columns_from_db()

    def _get_columns_from_db(self) -> Tuple:
        for columns in Query.get_columns(SCHEMA, self.name, COLUMN_METADATA):
            self._add_to_self(columns)

    def _add_to_self(self, columns: Tuple):
        column_metadata = dict(zip(COLUMN_METADATA, columns))
        column = Column(column_metadata)
        setattr(self, column_metadata['column_name'], column)
        self._columns[column_metadata['column_name']] = column

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, name: str):
        self._columns[name] = Column(name)

    @property
    def schema(self):
        return self._schema


class Column():
    def __init__(self, column_metadata: dict):
        self._metadata = dict()
        for key in column_metadata:
            setattr(self, key, column_metadata[key])   # To be considered
            self._metadata[key] = column_metadata[key]

    def get(self):
        return self


class Printer():
    def __init__(self, db: DBModel, schema_name: str, table_names: Tuple):
        self.db = db
        self.ct = ConsoleTable()
        self.table_names = table_names
        self.schema_name = schema_name
        self._table_objects = []
        self._printables = []
        self.print_tables_to_console()

    def print_tables_to_console(self):
        self._prepare_to_print()
        for table in self._printables:
            print(table, '\n')

    def _prepare_to_print(self):
        self._get_table_objects_from_db_model()
        self._serialize(self._get_columns())

    def _get_table_objects_from_db_model(self) -> List[Table]:
        for table_name in self.table_names:
            self._table_objects.append(
                self.db.schemas[self.schema_name].tables[table_name]
            )

    def _get_columns(self) -> Dict:
        tables_to_be_printed = dd(list)
        for table in self._table_objects:
            for column in table.columns.values():
                tables_to_be_printed[table.name].append(
                    [
                        column.column_name,
                        column.is_nullable,
                        column.data_type
                    ]
                )
        return tables_to_be_printed

    def _serialize(self, tables: Dict):
        for table_name, columns in tables.items():
            columns = [
                [x[0] for x in columns],
                [x[1] for x in columns],
                [x[2] for x in columns]
            ]
            self._printables.append(
                self.ct.make(
                    tuple(COLUMN_METADATA),
                    tuple(columns),
                    table_name.capitalize()
                )
            )

#
# Workbench for ideas TBC
#
"""
db = DBModel()


print(repr(db.schemas['home'].tables['home_measures']))

t = tuple(['home_measures', 'illuminance'])
Printer(db, 'home', t)
"""

t = Table('illuminance', 'home')
q = Query(t)
result = q.read({'room': 'duzy pokoj'})
import pdb
pdb.set_trace()

# Pomysl na db_driver - nadpisać obiekty Column wartościami
# kolejnosc t.columns to ts_id, illuminance, room
# t.columns['ts_id'] = result[0][0]
# t.columns['illuminance'] = result[0][1]
# t.columns[']