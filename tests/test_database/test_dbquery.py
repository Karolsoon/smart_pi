from decimal import Decimal
from datetime import datetime, timedelta

from pytz import timezone

import pytest

from tests.test_database.stub.postgresdriver_stub import pgDriverStub
from database.dbquery import Query
from GPIO.lcdprinter import HomeMode4x20


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


@pytest.fixture(scope='session')
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
            CREATE TABLE IF NOT EXISTS test_smart_home.illuminance (
                ts_id timestamptz NOT NULL,
                room varchar NOT NULL,
                illuminance int2 NULL,
                insert_ts timestamptz NOT NULL DEFAULT now()
            );
                INSERT INTO test_smart_home.home_measures 
                (ts_id, room, temperature, pressure, humidity, insert_ts) VALUES
                (now(), 'duzy pokoj', 26.1, 990, 75.1, now()),
                (now() - '2 days'::interval, 'trzeci pokoj', 99.9, 9999, NULL, now()),
                (now() - '90 seconds'::interval, 'pokoj dziewczyn', 99.9, NULL, NULL, now()),
                (now() - '91 seconds'::interval, 'duzy pokoj', 99.9, NULL, NULL, now()),
                (now() - '30 seconds'::interval, 'trzeci pokoj', 99.9, 9999, NULL, now()),
                (now(), 'pokoj dziewczyn', 27.1, NULL, NULL, now()),
                (now(), 'trzeci pokoj', 28.1, 1017, NULL, now());

                INSERT INTO test_smart_home.illuminance 
                (ts_id, room, illuminance, insert_ts) VALUES
                (now(), 'duzy pokoj', 99, now()),
                (now(), 'trzeci pokoj', 100, now()),
                (now() - '1 second'::interval, 'duzy pokoj', 999, now()),
                (now() - '91 seconds'::interval, 'duzy pokoj', 999, now());

                CREATE OR REPLACE VIEW test_smart_home.daily_measures AS (
                WITH daily AS (
                SELECT date_trunc('hour'::text, hm.ts_id) AS date_time,
                    round(avg(hm.pressure), 0) AS pressure_avg,
                    AVG(AVG(pressure)) OVER(ORDER BY DATE_TRUNC('hour', ts_id) DESC GROUPS 5 PRECEDING ) AS SMA_5H,
                    round(avg(hm.temperature), 2) AS temperature
                FROM test_smart_home.home_measures hm
                WHERE hm.ts_id >= (now() - '5 days'::interval) AND hm.ts_id <= now() AND lower(hm.room::text) = 'duzy pokoj'::text
                GROUP BY (date_trunc('hour'::text, hm.ts_id))
                ORDER BY (date_trunc('hour'::text, hm.ts_id))
                )

                SELECT 
                    TO_CHAR(date_time, 'YYYY-MM-DD HH24:MI:SS') AS ts,
                    round(SMA_5H, 4) AS pressure_SMA,
                    LAG(round(SMA_5H, 5), 3) OVER() AS pressure_lag5,
                    LAG(round(SMA_5H, 1), 3) OVER() AS pressure_lag1,
                    pressure_avg,
                --	CASE 
                --	WHEN round(SMA_5H, 1) % 1 BETWEEN 0 AND 0.29 THEN trunc(SMA_5H)
                --	WHEN round(SMA_5H, 1) % 1 BETWEEN 0.3 AND 0.69 THEN trunc(SMA_5H) + 0.5
                --	WHEN round(SMA_5H, 1) % 1 BETWEEN 0.7 AND 0.99 THEN trunc(SMA_5H) + 1
                --	END,
                    temperature
                FROM 
                    daily
                );
                CREATE OR REPLACE VIEW test_smart_home.pressure_trend AS (
                SELECT 
                    CASE
                        WHEN d.pressure_SMA >= pressure_lag5 AND d.pressure_SMA > d.pressure_lag1 THEN 'UP'
                        WHEN d.pressure_SMA <= pressure_lag5 AND d.pressure_SMA < d.pressure_lag1 THEN 'DOWN'
                    END AS pressure_trend,
                    'trzeci pokoj' AS room
                FROM 
                    test_smart_home.daily_measures d
                WHERE ts = TO_CHAR(DATE_TRUNC('hour', now()), 'YYYY-MM-DD HH24:MI:SS')
                );
        """
        conn.cursor.execute(query)
        conn.connection.commit()
        yield True

        query = """
            DROP TABLE IF EXISTS test_smart_home.home_measures CASCADE;
            DROP TABLE IF EXISTS test_smart_home.illuminance CASCADE;
        """
        conn.cursor.execute(query)
        conn.connection.commit()


@pytest.fixture(scope='function')
def pressure_history(valid_credentials):
    with pgDriverStub(valid_credentials) as conn:
        query = """
            INSERT INTO test_smart_home.home_measures
            (ts_id, room, temperature, pressure, humidity, insert_ts) VALUES
            (now(), 'duzy pokoj', 0, 1020, NULL, now()),
            (now() - '1 hour'::interval, 'duzy pokoj', 0, 1019, NULL, now()),
            (now() - '2 hours'::interval, 'duzy pokoj', 0, 1019, NULL, now()),
            (now() - '3 hours'::interval, 'duzy pokoj', 0, 1018, NULL, now()),
            (now() - '4 hours'::interval, 'duzy pokoj', 0, 1018, NULL, now()),
            (now() - '5 hours'::interval, 'duzy pokoj', 0, 1017, NULL, now()),
            (now() - '6 hours'::interval, 'duzy pokoj', 0, 1016, NULL, now());
        """
        conn.cursor.execute(query)
        conn.connection.commit()
        yield True

@pytest.fixture(scope='function')
def querymaker(valid_credentials, setup):
    pgdriver = pgDriverStub(valid_credentials)
    return Query(pgdriver, 'test_smart_home')


def test_get_schemas_returns_correct_schemas(querymaker):
    dataset = querymaker.get_schemas(excluded=EXCLUDED_SCHEMAS)
    assert ['test_smart_home'] in dataset


def test_get_tables_returns_correct_tables(querymaker):
    # if setup:
    dataset = querymaker.get_tables(table_type='base table')
    assert ['home_measures'] in dataset


def test_get_home_measires_returns_most_recent(querymaker):
    datasets = querymaker.get_latest('home_measures')
    # Most recent dataset for room1
    assert datasets[0][1].replace(tzinfo=None) <= datetime.now() + timedelta(seconds=90)
    assert datasets[0][2:6] == ['duzy pokoj', Decimal('26.10'), 990, Decimal('75.1')]

    # Most recent dataset for room 2
    assert datasets[1][1].replace(tzinfo=None) <= datetime.now() + timedelta(seconds=90)
    assert datasets[1][2:6] == ['pokoj dziewczyn', Decimal('27.10'), None, None]

    # Most recent dataset for room 3
    assert datasets[2][1].replace(tzinfo=None) <= datetime.now() + timedelta(seconds=90)
    assert datasets[2][2:6] == ['trzeci pokoj', Decimal('28.10'), 1017, None]


def test_get_illuminance_returns_most_recent(querymaker):
    datasets = querymaker.get_latest('illuminance')
    # Most recent dataset for room1
    assert datasets[0][1].replace(tzinfo=None) <= datetime.now() + timedelta(seconds=90)
    assert datasets[0][2:4] == ['duzy pokoj', 99]

    # Most recent dataset for room 2
    assert datasets[1][1].replace(tzinfo=None) <= datetime.now() + timedelta(seconds=90)
    assert datasets[1][2:4] == ['trzeci pokoj', 100]


def test_data_after_insert_is_available_in_db(querymaker):
    ts_id = datetime.now().astimezone(timezone('Europe/Berlin'))
    insert_dataset = (
            {
                'home_measures': {
                        'ts_id': f'\'{ts_id}\'',
                        'room': '\'duzy pokoj\'',
                        'temperature': 99.9,
                        'pressure': 9999,
                        'humidity': 99,
                        'insert_ts': '\'now()\''
                }
            },
            {
                'home_measures': {
                        'ts_id': f'\'{ts_id}\'',
                        'room': '\'trzeci pokoj\'',
                        'temperature': 99.9,
                        'pressure': 9999,
                        'humidity': 'NULL',
                        'insert_ts': '\'now()\''
                }
            },
            {
                'home_measures': {
                        'ts_id': f'\'{ts_id}\'',
                        'room': '\'pokoj dziewczyn\'',
                        'temperature': 99.9,
                        'pressure': 'NULL',
                        'humidity': 'NULL',
                        'insert_ts': '\'now()\''
                }
            }
    )
    querymaker.insert_sensor_data(insert_dataset)
    datasets_home_measures = querymaker.get_latest('home_measures')
    assert datasets_home_measures[0][1] == ts_id
    assert datasets_home_measures[1][1] == ts_id
    assert datasets_home_measures[2][1] == ts_id


def test_can_insert_rows_into_different_tables_at_the_same_time(querymaker):
    ts_id = datetime.now().astimezone(timezone('Europe/Berlin'))
    insert_dataset = (
            {
                'home_measures': {
                        'ts_id': f'\'{ts_id}\'',
                        'room': '\'aaa home_measures\'',
                        'temperature': 99.9,
                        'pressure': 9999,
                        'humidity': 99,
                        'insert_ts': '\'now()\''
                }
            },
            {
                'illuminance': {
                        'ts_id': f'\'{ts_id}\'',
                        'room': '\'aaa illuminance\'',
                        'illuminance': 999,
                        'insert_ts': '\'now()\''
                }
            }
    )
    querymaker.insert_sensor_data(insert_dataset)
    datasets = (
          querymaker.get_latest('illuminance')
        + querymaker.get_latest('home_measures')
    )
    for dataset in datasets:
        if dataset['room'] in ['aaa home_measures', 'aaa illuminance']:
            assert dataset['ts_id'] == ts_id


def test_row_columns_are_accesible_by_name(querymaker):
    dataset = querymaker.get_latest('home_measures')
    assert dataset[0]['temperature'] == Decimal('99.9')


def test_transformed_queryset_is_dict(querymaker: Query):
    transformed_dataset = querymaker.get_transformed_latest(('home_measures',))
    assert isinstance(transformed_dataset, dict)


def test_transformes_queryset_is_grouped_by_rooms(querymaker):
    #
    # DO NOT ADD TESTS WHICH INSERT DATA TO THE TEST DB >>>BEFORE<<< THIS TEST
    #
    expected_rooms = ['aaa home_measures', 'duzy pokoj', 'pokoj dziewczyn', 'trzeci pokoj']
    transformed_dataset = querymaker.get_transformed_latest(('home_measures',))
    assert list(transformed_dataset.keys()) == expected_rooms


def test_transformed_queryset_is_complete(querymaker):
    expected_dataset = {
        'aaa home_measures': {
            'humidity': '99.0',
            'pressure': '9999',
            'temperature': '99.90'
        },
        'aaa illuminance': {
            'illuminance': '999'
        },
        'duzy pokoj': {
            'humidity': '99.0',
            'illuminance': '99',
            'pressure': '9999',
            'temperature': '99.90'
        },
        'pokoj dziewczyn': {
            'temperature': '99.90'
        },
        'trzeci pokoj': {
            'illuminance': '100',
            'pressure': '9999', 
            'temperature': '99.90'
        }
    }
    transformed_dataset = querymaker.get_transformed_latest(
        ('home_measures','illuminance'),
        HomeMode4x20.template
        )
    assert transformed_dataset == expected_dataset


def test_pressure_trend_returns_correct_arrow(querymaker, pressure_history):
    if pressure_history:
        trend = querymaker.get_pressure_trend()
        assert trend[0][0] == 'UP'
