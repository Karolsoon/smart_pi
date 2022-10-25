#from RPi_GPIO_i2c_LCD import lcd


class LCDPrinter:

    _lines = {}

    def __init__(self, lcd) -> None:
        self.lcd = lcd

    def _validate_new_lines(self, new_lines: dict) -> None:
        self._is_dict(new_lines)
        self._is_correct_length(new_lines)
        self._is_correct_content_length(new_lines)

    def _is_dict(self, new_lines: dict) -> None:
        if not isinstance(new_lines, dict):
            raise TypeError(
                f'Expected dict, got {type(new_lines).__name__} instead.'
            )

    def _is_correct_length(self, new_lines):
        if not (len(new_lines) >= 0 and len(new_lines) <= 4):
            raise ValueError(
                f'Exceeded max number of lines: {len(new_lines)}. Limit is 4'
            )

    def _is_correct_content_length(self, new_lines):
        for line_number, line in new_lines.items():
            if len(line) > 20:
                raise ValueError(
                    f'Line {line_number} exceeds 20 characters. Is {len(line)}.'
                )

    def clear(self) -> None:
        empty_lines = {k + 1: (' ' * 20) for k in range(len(self._lines))}
        self.set_lines(empty_lines)

    def clear_line(self, line: int) -> None:
        self.set_lines({line: ' ' * 20})

    def print_on_lcd(self, line_number: int, line_text: str) -> None:
        # @TODO Change function 'set' to set_line in source code of lcd.HD44780
        self.lcd.set(line_text, line_number)

    def get_lines(self):
        return self._lines

    def set_lines(self, new_lines: dict):
        self._validate_new_lines(new_lines)
        for line_number, line in new_lines.items():
            self._lines[line_number] = line
            self.print_on_lcd(line_number, line)
