from typing import Tuple, List

from database.db_exceptions.too_many_columns_error import TooManyColumnsError
from database.db_exceptions.too_many_headers_error import TooManyHeadersError

from prettytable import PrettyTable


class ConsoleTable():
    def __init__(self):
        self.pt = PrettyTable()

    def make(self, headers: Tuple[str], columns: Tuple[List], title=None) -> str:
        self._validate(headers, columns)
        columns_lengths = self._get_columns_lengths(columns)
        if self._is_len_uneven(columns_lengths):
            columns = self._equalize_lengths(columns, columns_lengths)
        pt = PrettyTable()
        pt.title = title
        result = self._return_none_or_table(headers, columns, pt)

        return result

    @staticmethod
    def is_equal_length(value, value_compared):
        return len(value) == len(value_compared)

    def _validate(self, headers, columns):
        self._validate_not_empty(headers, 'headers')
        self._validate_not_empty(columns, 'columns')
        self._validate_data_type(headers, 'headers')
        self._validate_data_type(columns, 'columns')
        self._validate_column_and_header_count(headers, columns)

    def _validate_not_empty(self, data, parameter_name):
        if self._is_empty_or_none(data):
            raise ValueError(f'"{parameter_name}" cannot be empty')

    def _is_empty_or_none(self, data):
        return data is None or len(data) == 0

    def _validate_data_type(self, data, parameter_name):
        if self._is_not_tuple(data):
            raise TypeError(
                f'"{parameter_name}" should be tuple, got {type(data).__name__} instead'
            )

    def _is_not_tuple(self, data):
        return not isinstance(data, tuple)

    def _validate_column_and_header_count(self, headers, columns):
        if not self.is_equal_length(headers, columns):
            self._raise_exception_based_on_longer_dataset(headers, columns)

    def _raise_exception_based_on_longer_dataset(self, headers, columns):
        if len(headers) > len(columns):
            raise TooManyHeadersError('More headers than columns provided')
        raise TooManyColumnsError('More columns than headers provided')

    def _get_columns_lengths(self, columns: Tuple[List]) -> Tuple[int]:
        return tuple(len(x) for x in columns)

    def _is_len_uneven(self, columns_lenght):
        return len(set(columns_lenght)) % 2 == 1

    def _return_none_or_table(self, headers: Tuple[str],
            columns: Tuple[List], pt: PrettyTable):
        if headers:
            return self._add_column(headers, columns, pt)

    def _equalize_lengths(self, columns, columns_lengths):
        equalized_columns = []
        for column in columns:
            l = lambda x: x + [' '] * (max(columns_lengths) - len(x)) 
            equalized_columns.append(l(column))
        return equalized_columns

    def _add_column(self, headers, columns, pt: PrettyTable):
        if columns:
            for i, header in enumerate(headers):
                pt.add_column(header.capitalize(), columns[i])
        return pt
