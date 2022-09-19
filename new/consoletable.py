from prettytable import PrettyTable

class ConsoleTable():
    def __init__(self):
        self.pt = PrettyTable()
    
    @classmethod
    def make(cls, headers: tuple, columns: tuple, title=None):
        columns_lengths = cls._get_columns_lengths(cls, columns)
        if cls._check_if_len_is_not_equal(cls, columns_lengths):
            columns = cls._equalize_lengths(
                cls, columns, columns_lengths)
        pt = PrettyTable()
        pt.title = title
        return cls._return_none_or_table(cls, headers, columns, pt)

    def _get_columns_lengths(self, columns):
        return tuple(len(x) for x in columns)

    def _check_if_len_is_not_equal(self, columns_lenght):
        if len(set(columns_lenght)) != 1:
            return True
        return False

    def _return_none_or_table(self, headers, columns, pt):
        if headers:
            return self._add_column(self, headers, columns, pt)
        return None

    def _equalize_lengths(self, columns, columns_lengths):
        equalized_columns = []
        for column in columns:
            l = lambda x: x + [' '] * (max(columns_lengths) - len(x)) 
            equalized_columns.append(l(column))
        return equalized_columns
    
    def _add_column(self, headers, columns, pt: PrettyTable):
        if columns:
            for i in range(len(headers)):
                pt.add_column(headers[i].capitalize(), columns[i])
        return pt
