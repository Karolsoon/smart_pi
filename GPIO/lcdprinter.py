import datetime

#from RPi_GPIO_i2c_LCD import lcd as GPIO_LCD


class LCDPrinter:

    LINE_LENGTH = 20
    LINE_QUANTITY = 4
    _lines = {k + 1: ' ' * 20 for k in range(4)}

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
        if not (len(new_lines) >= 0 and len(new_lines) <= self.LINE_QUANTITY):
            raise ValueError(
                f'Exceeded max number of lines: {len(new_lines)}. Limit is {self.LINE_QUANTITY}'
            )

    def _is_correct_content_length(self, new_lines):
        for line_number, line in new_lines.items():
            if len(line) > self.LINE_LENGTH:
                raise ValueError(
                    f'Line {line_number} exceeds {self.LINE_LENGTH} characters. Is {len(line)}.'
                )

    def clear(self) -> None:
        empty_lines = {
            k + 1: (' ' * self.LINE_LENGTH)
            for k
            in range(len(self._lines))
        }
        self.set_lines(empty_lines)

    def clear_line(self, line: int) -> None:
        self.set_lines({line: ' ' * self.LINE_LENGTH})

    def print_on_lcd(self, line_number: int, line_text: str) -> None:
        # @TODO Change function 'set' to set_line in source code of lcd.HD44780
        self.lcd.set(line_text, line_number)

    def get_lines(self):
        return self._lines

    def set_lines(self, new_lines: dict):
        self._validate_new_lines(new_lines)
        for line_number, line in new_lines.items():
            if self._lines[line_number] != line:
                self._lines[line_number] = line
                self.print_on_lcd(line_number, line)


class HomeMode4x20:
    arrows = {'UP': '↑', 'DOWN': '↓', 'CONSTANT': '-', 'both': '⇅'}
    template = {
        #   12345678901234567890
        1: 'DD.MM.YYYY xxxxhPa ↑',
        2: 'DP:xx.xC xxxLX xx.x%',
        3: 'DZ:xx.xC    TP:xx.xC',
        4: '                    '
    }

    def get_required_tables(self):
        return ('home_measures', 'illuminance')

    def build_lines(self, dataset: dict[dict], pressure_trend: str):
        date = datetime.date.today().isoformat().split('-')
        date_formatted = f'{date[2]}.{date[1]}.{date[0]}'
        return {
            1: f"{date_formatted} {dataset['duzy pokoj']['pressure']}hPa {self.arrows[pressure_trend]}",
            2: f"DP:{dataset['duzy pokoj']['temperature']}C  {dataset['duzy pokoj']['illuminance']}lx {dataset['duzy pokoj']['humidity'][:2]}%",
            3: f"DZ:{dataset['pokoj dziewczyn']['temperature']}C  TP:{dataset['trzeci pokoj']['temperature']}C",
            4: ' ' * 20
        }
