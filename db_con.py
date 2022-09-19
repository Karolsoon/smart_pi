import psycopg2
import datetime
from new import credentials
from time import sleep


USER = credentials.USER
PASSWORD = credentials.PASSWORD
HOST = credentials.HOST
PORT = credentials.PORT
DBNAME = 'smart_home'


class Connector:
    def __init__(self, schema='home'):
        self.conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=DBNAME,
            user=USER,
            password=PASSWORD
        )
        self.schema = schema
        self.cur = self.conn.cursor()
        self.cur.execute(f'SET search_path TO {self.schema}')

    def __enter__(self):
        return self

    def __exit__(self, exception, value, trace):
        if exception or value:
            self.conn.rollback()
            self.cur.close()
            self.conn.close()
            print(f'DB Error: {exception}, {value}, {trace}')
            return 1
        else:
            self.conn.commit()
            self.cur.close()
            self.conn.close()

    def retrieve_data(self, column, room=None, table='home_measures'):
        """
        Retrieves data from home_measures table. If no data retrieved None value
        is returned.

        column - usually the measure name like temperature, pressure, humidity
        """
        query = f"""
            SELECT {column}
            FROM {self.schema}.{table}
            WHERE ts_id > (CURRENT_TIMESTAMP - '90 seconds'::INTERVAL)
            """
        
        if room:
            query = query + f'AND lower(room) = lower(\'{room}\')'
        
        query = query + 'ORDER BY ts_id DESC LIMIT 1'

        self.cur.execute(query)
        try:
            result = self.cur.fetchone()
        except psycopg2.ProgrammingError:
            print(f'{datetime.datetime.now()} - Query returned no results')
            result = None
        return result[0] if result else '----'


    def insert_data(self, room, data, data_type=None):
        """
        Inserts sensor measurements, room name and current timestamp into DB.
        
        Currently supports 3 sensor values: temperature, pressure, humidity.
        """
        try:
            self.cur.execute(
                f"""INSERT INTO home.home_measures (ts_id, room, temperature, pressure, humidity) VALUES
                (CURRENT_TIMESTAMP, '{room}', {data[0]}, {data[1]}, {data[2]})""")
        except psycopg2.OperationalError:
            print(f'{datetime.datetime.now()} - DB is busy or down.')
            sleep(5)


    def insert_lux_data(self, room, data):
        """
        Insert luxmeter data, room and current timestamp into DB.
        """
        try:
            self.cur.execute(
                f"""INSERT INTO home.illuminance (ts_id, room, illuminance) VALUES
                (CURRENT_TIMESTAMP, '{room}', {data})""")
        except psycopg2.OperationalError:
            print(f'{datetime.datetime.now()} - DB is busy or down.')

    def insert_pip_data(self, person, is_light):
        """
        Insert pip data and current timestamp into DB.
        """
        try:
            self.cur.execute(
                f"""INSERT INTO home.pip (ts_id, person, is_light) VALUES
                (CURRENT_TIMESTAMP, '{person}', {is_light})""")
        except psycopg2.OperationalError:
            print(f'{datetime.datetime.now()} - DB is busy or down - insert_pip')


