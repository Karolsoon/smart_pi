from prettytable import PrettyTable

class ConsoleTable():
    pt = PrettyTable()

    def __init__(self):
        pass
    
    @classmethod
    def make_table_by_columns(cls, headers, columns):
        columns_lengths = cls._get_columns_lengths(cls, columns)
        if cls._check_if_len_is_not_equal(cls, columns_lengths):
            columns = cls._equalize_lengths(
                cls, columns, columns_lengths)

        return cls._add_column(cls, headers, columns)

    def _check_if_len_is_not_equal(self, columns_lenght):
        if len(set(columns_lenght)) != 1:
            return True
        return False

    def _get_columns_lengths(self, columns):
        return [len(x) for x in columns]

    def _equalize_lengths(self, columns, columns_lengths):
        equalized_columns = []
        for column in columns:
            l = lambda x: x + [' '] * (max(columns_lengths) - len(x)) 
            print(l(column))
            equalized_columns.append(l(column))
        return equalized_columns
    
    def _add_column(self, headers, columns):
        for i in range(len(headers)):
            self.pt.add_column(headers[i], columns[i])
        return self.pt