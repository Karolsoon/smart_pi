#from RPi_GPIO_i2c_LCD import lcd

"""
Mock class for development.
My computer has no GPIO pins :_)
"""

class lcd:
    class HD44780:
        def __init__(self, i2caddress):
            if i2caddress == 0x27:
                self.i2caddress = i2caddress
            else:
                raise ConnectionError('LCD screen is not connected')
        def set_line(self, string, line):
            pass

"""
End of Mock class
"""

class LCDPrinter(lcd.HD44780):
    def __init__(self, i2caddress) -> None:
        self._lines = {}
        super().__init__(i2caddress)

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, new_lines):
        self.__validate_new_lines(new_lines)
        for line_number, line in new_lines.items():
            self._lines[line_number] = line
            self._print_on_lcd(line_number, line)

    def __validate_new_lines(self, new_lines):
        self.__is_list(new_lines)
        self.__is_correct_length(new_lines)
        self.__is_correct_content_length(new_lines)

    def __is_list(self, new_lines):
        if not isinstance(new_lines, dict):
            raise TypeError(
                f'Expected dict, got {type(new_lines).__name__} instead.'
            )

    def __is_correct_length(self, new_lines):
        if not (len(new_lines) >= 0 and len(new_lines) <= 4):
            raise ValueError(
                f'Exceeded max number of lines: {len(new_lines)}. Limit is 4'
            )

    def __is_correct_content_length(self, new_lines):
        for line_number, line in new_lines.items():
            if len(line) > 20:
                raise ValueError(
                    f'Line {line_number} exceeds 20 characters. Is {len(line)}.'
                )

    def clear(self):
        for i in range(len(self.lines)):
            self.clear_line(i + 1)

    def clear_line(self, line):
        self.lines = {line: ' ' * 20}

    def _print_on_lcd(self, line_number, line_text):
        # @TODO Change set to set_line in source code of lcd.HD44780
        self.set_line(line_text, line_number)
