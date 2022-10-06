class ColumnDoesNotExist(Exception):
    pass


class TooManyValuesToInsert(Exception):
    pass


class ConstraintViolation(Exception):
    pass


class NotNullViolation(ValueError):
    pass


class UniqueViolation(ConstraintViolation):
    pass