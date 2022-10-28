from psycopg2 import OperationalError
import pytest
from decimal import Decimal

from tests.test_database.stub.postgresdriver_stub import pgDriverStub


@pytest.fixture(scope='function')
def valid_credentials():
    yield {
        'host': '127.0.0.1',
        'port': '5432',
        'dbname': 'test_db',
        'user': 'postgres',
        'password': 'postgres'
    }


@pytest.fixture(scope='function')
def invalid_host():
    yield {
        'host': '192.168.0.199',
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
        """
        conn.cursor.execute(query)
        conn.connection.commit()
        yield True


        query = """
            DROP TABLE IF EXISTS test_smart_home.home_measures CASCADE;
        """
        conn.cursor.execute(query)
        conn.connection.commit()


def test_connects_to_database(valid_credentials):
    with pgDriverStub(valid_credentials) as conn:
        assert conn.connection.status == 1


def test_invalid_host_address_raises_exception(invalid_host):
    with pytest.raises(OperationalError) as exc:
        with pgDriverStub(invalid_host) as conn:
            pass
    expected = (
        'timeout expired\n',
        'could not connect to server:'
    )
    assert str(exc.value).startswith(expected)


def test_valid_transaction_is_successfully_commited(valid_credentials, setup):
    if setup:
        with pgDriverStub(valid_credentials) as conn:
            # when
            query = """
                INSERT INTO test_smart_home.home_measures 
                (ts_id, room, temperature, pressure, humidity, insert_ts) VALUES
                (now(), 'duzy pokoj', 26.1, 1015, 73.5, now())
            """
            conn.cursor.execute(query)
            conn.connection.commit()

            # given
            query = """
                SELECT
                    ts_id, room, temperature, pressure, humidity, insert_ts
                FROM
                    test_smart_home.home_measures
                ORDER BY 
                    ts_id DESC
                LIMIT 1;
            """
            conn.cursor.execute(query)
            dataset = conn.cursor.fetchone()
            # then
            assert dataset[1:5] == ['duzy pokoj', Decimal('26.1'), 1015, Decimal('73.5')]
