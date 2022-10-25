import pytest

from  database.consoletable import ConsoleTable


@pytest.fixture(scope='function')
def console_table():
    yield ConsoleTable()

@pytest.mark.parametrize('headers,columns,title,expected', [
    (
        ('id',),
        (['x'],),
        None,
        '+-----+\n| None |\n+-----+\n|  Id |\n+-----+\n|  x  |\n+-----+'
    ),
    (
        ('name', 'surname', 'random'),
        (['bob', 'jimmy'], ['doe', 'boe'], ['1', '2']),
        'A_title',
        '+--------------------------+\n|         A_title          |\n+-------+---------+--------+\n|  Name | Surname | Random |\n+-------+---------+--------+\n|  bob  |   doe   |   1    |\n| jimmy |   boe   |   2    |\n+-------+---------+--------+'
    )
])
def test_make(console_table, headers, columns, title, expected):
    printed_table = console_table.make(headers, columns, title)
    assert printed_table.get_string() == expected


def test_raises_exception_when_headers_is_not_tuple(console_table):
    with pytest.raises(Exception) as exp:
        console_table.make(
            headers=['name', 'age'],
            columns=(['bob', 'alice'], ['50', '37']),
            title='Employees'
        )
    assert str(exp.value) == '"headers" should be tuple, got list instead'


def test_raises_exception_when_columns_is_not_tuple(console_table):
    with pytest.raises(Exception) as exp:
        console_table.make(
            headers=('name', 'age'),
            columns=[['bob', 'alice'], ['50', '37']],
            title='Employees'
        )
    assert str(exp.value) == '"columns" should be tuple, got list instead'


def test_raises_exception_when_more_columns_than_headers(console_table):
    with pytest.raises(Exception) as exp:
        console_table.make(
            headers=('Name', 'Surname'),
            columns=tuple(['Bob', 'Doe', 'Male']),
            title='People')
    assert str(exp.value) == 'More columns than headers provided'


def test_raises_exception_when_more_headers_than_columns(console_table):
    with pytest.raises(Exception) as exp:
        console_table.make(
            headers=('Name', 'Surname', 'Gender'),
            columns=tuple(['Bob', 'Doe']),
            title='People')
    assert str(exp.value) == 'More headers than columns provided'


def test_raises_exception_when_columns_is_empty(console_table):
    with pytest.raises(Exception) as exp:
        console_table.make(
            headers=('Name', 'Surname', 'Gender'),
            columns=(),
            title='People')
    assert str(exp.value) == '"columns" cannot be empty'


def test_raises_exception_when_headers_is_empty(console_table):
    with pytest.raises(Exception) as exp:
        console_table.make(
            headers=(),
            columns=tuple(['Bob', 'Doe']),
            title='People')
    assert str(exp.value) == '"headers" cannot be empty'
