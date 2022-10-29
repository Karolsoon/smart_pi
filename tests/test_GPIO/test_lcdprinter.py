import pytest
import datetime

from tests.test_GPIO.stub.lcd_stub import LCDStub
from tests.test_database.test_dbquery import querymaker, setup, valid_credentials
from GPIO.lcdprinter import HomeMode4x20, LCDPrinter


@pytest.fixture(scope='function')
def printer():
    lcd = LCDStub()
    yield LCDPrinter(lcd)


@pytest.fixture(scope='function')
def correct_lines():
    lines_to_print = {
        1: '12345678901234567890',
        2: '12345678901234567890',
        3: '12345678901234567890',
        4: '12345678901234567890'
    }
    yield lines_to_print


@pytest.fixture(scope='function')
def incorrect_lines():
    lines_to_print = {
        1: '1',
        2: '2',
        3: '3',
        4: '123456789012345678901',
        5: '5',
    }
    yield lines_to_print


def test_lines_to_print_is_a_dict(correct_lines, printer):
    printer.set_lines(correct_lines)
    assert isinstance(printer.get_lines(), dict)


def test_raises_exception_when_lines_are_not_a_dict(incorrect_lines, printer):
    with pytest.raises(Exception) as exp:
        printer.set_lines(tuple(incorrect_lines.values()))
    assert str(exp.value) == ('Expected dict, got tuple instead.')


def test_dict_with_lines_has_correct_number_of_lines(correct_lines, printer):
    printer.set_lines(correct_lines)
    assert len(printer.get_lines()) >= 0
    assert len(printer.get_lines()) <= 4


def test_raise_exception_when_incorrect_dict_length(incorrect_lines, printer):
    with pytest.raises(Exception) as exp:
        printer.set_lines(incorrect_lines)
    assert str(exp.value) == (
        f'Exceeded max number of lines: {len(incorrect_lines)}. Limit is 4'
        )


def test_lines_have_correct_length(correct_lines, printer):
    printer.set_lines(correct_lines)
    for line in printer.get_lines().values():
        assert len(line) >= 0
        assert len(line) <= 20


def test_raise_exception_when_incorrect_content_length(incorrect_lines, printer):
    with pytest.raises(Exception) as exp:
        printer.set_lines({2: incorrect_lines[4]})
        assert str(exp.value) == (
            f'Exceeded max number of lines: {len(max(incorrect_lines))}. Limit is 4'
        )


def test_clear(printer):
    printer.clear()
    for line in printer.get_lines().values():
        assert line == ' ' * 20


def test_clear_line(printer):
    printer.clear_line(2)
    assert printer.get_lines()[2] == ' ' * 20


def test_print(printer):
    # @TODO No idea how to do that
    pass

#
# TEST HomeMode4x20
#

def test_reuired_table_returns_tuple_of_table_names():
    home = HomeMode4x20()
    assert home.get_required_tables() == ('home_measures', 'illuminance')


def test_build_lines_returns_dict(querymaker):
    dataset = querymaker.get_transformed_latest(('home_measures','illuminance'))
    home = HomeMode4x20()
    lines = home.build_lines(dataset, 'UP')
    date = datetime.date.today().isoformat().split('-')
    date_formatted = f'{date[2]}.{date[1]}.{date[0]}'
    assert lines == {
        1: f'{date_formatted}  990hPa ↑',
        2: 'DP:26.1C  99lx 75.1%',
        3: 'DZ:27.1C    TP:28.1C',
        4: '                    '
    }
