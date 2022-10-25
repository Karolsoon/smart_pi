from decimal import Decimal
from datetime import datetime, timedelta
from pytz import timezone

import pytest

from tests.test_database.stub.postgresdriver_stub import pgDriverStub
from database.dbquery import Query


EXCLUDED_SCHEMAS = """'pg_catalog', 'information_schema', 'pg_toast'"""


@pytest.fixture(scope='function')
def valid_credentials():
    yield {
        'host': '127.0.0.1',
        'port': '5432',
        'dbname': 'test_db',
        'user': 'postgres',
        'password': 'postgres'
    }


@pytest.fixture(scope='module')
def setup():
    credentials = {
        'host': '127.0.0.1',
        'port': '5432',
        'dbname': 'test_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    with pgDriverStub(credentials) as conn:
        query = """
            CREATE SCHEMA IF NOT EXISTS test_smart_home;
            DROP TABLE IF EXISTS test_smart_home.home_measures CASCADE;
            CREATE TABLE IF NOT EXISTS test_smart_home.home_measures (
                ts_id timestamptz NOT NULL,
                room varchar NOT NULL,
                temperature numeric(4, 2) NOT NULL,
                pressure int2 NULL,
                humidity NUMERIC(3,1) NULL,
                insert_ts timestamptz NOT NULL DEFAULT now()
            );
                INSERT INTO test_smart_home.home_measures 
                (ts_id, room, temperature, pressure, humidity, insert_ts) VALUES
                (now(), 'duzy pokoj', 26.1, NULL, NULL, now()),
                (now() - '2 days'::interval, 'trzeci pokoj', 99.9, 9999, NULL, now()),
                (now() - '90 seconds'::interval, 'pokoj dziewczyn', 99.9, NULL, NULL, now()),
                (now() - '91 seconds'::interval, 'duzy pokoj', 99.9, NULL, NULL, now()),
                (now() - '30 seconds'::interval, 'trzeci pokoj', 99.9, 9999, NULL, now()),
                (now(), 'pokoj dziewczyn', 26.1, NULL, NULL, now()),
                (now(), 'trzeci pokoj', 26.1, 1017, NULL, now())
        """
        conn.cursor.execute(query)
        conn.connection.commit()

        yield True

        query = """
            DROP TABLE IF EXISTS test_smart_home.home_measures CASCADE;
        """
        conn.cursor.execute(query)
        conn.connection.commit()


@pytest.fixture(scope='function')
def querymaker(valid_credentials):
    pgdriver = pgDriverStub(valid_credentials)
    return Query(pgdriver, 'test_smart_home')


def test_get_schemas_returns_correct_schemas(querymaker):
    dataset = querymaker.get_schemas(excluded=EXCLUDED_SCHEMAS)
    assert ('test_smart_home',) in dataset


def test_get_tables_returns_correct_tables(querymaker, setup):
    if setup:
        dataset = querymaker.get_tables(table_type='base table')
    assert ('home_measures',) in dataset


def test_query_returns_only_most_recent_data_per_sensor(querymaker):
    datasets = querymaker.get_latest_home_measures()
    # Most recent dataset for room1
    assert datasets[0][0].replace(tzinfo=None) <= datetime.now() + timedelta(seconds=90)
    assert datasets[0][1:5] == ('duzy pokoj', Decimal('26.10'), None, None)

    # Most recent dataset for room 2
    assert datasets[1][0].replace(tzinfo=None) <= datetime.now() + timedelta(seconds=90)
    assert datasets[0][1:5] == ('duzy pokoj', Decimal('26.10'), None, None)

    # Most recent dataset for room 3
    assert datasets[2][0].replace(tzinfo=None) <= datetime.now() + timedelta(seconds=90)
    assert datasets[0][1:5] == ('duzy pokoj', Decimal('26.10'), None, None)


def test_data_after_insert_is_available_in_db(querymaker):
    ts_id = datetime.now().astimezone(timezone('Europe/Berlin'))
    insert_dataset = {
        1: {
                'ts_id': f'\'{ts_id}\'',
                'room': '\'duzy pokoj\'',
                'temperature': 99.9,
                'pressure': 9999,
                'humidity': 99,
                'insert_ts': '\'now()\''
            },
        2: {
                'ts_id': f'\'{ts_id}\'',
                'room': '\'trzeci pokoj\'',
                'temperature': 99.9,
                'pressure': 9999,
                'humidity': 99,
                'insert_ts': '\'now()\''
            },
        3: {
                'ts_id': f'\'{ts_id}\'',
                'room': '\'pokoj dziewczyn\'',
                'temperature': 99.9,
                'pressure': 9999,
                'humidity': 99,
                'insert_ts': '\'now()\''
            },
    }
    querymaker.insert_sensor_data('home_measures', insert_dataset)
    datasets = querymaker.get_latest_home_measures()
    assert datasets[0][0] == ts_id
    assert datasets[1][0] == ts_id
    assert datasets[2][0] == ts_id
