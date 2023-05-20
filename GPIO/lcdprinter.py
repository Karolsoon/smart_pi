import datetime

from RPi_GPIO_i2c_LCD import lcd as GPIO_LCD


class LCDPrinter():

    LINE_LENGTH = 20
    LINE_QUANTITY = 4
    _lines = {k + 1: ' ' * 20 for k in range(4)}

    def __init__(self, lcd: GPIO_LCD) -> None:
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
                    f'Line {line_number} exceeds {self.LINE_LENGTH} characters. Is {len(line)}, "{line}".'
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
        self._validate_new_lines(self._cleanse(new_lines))
        for line_number, line in new_lines.items():
            if self._lines[line_number] != line:
                self._lines[line_number] = line
                self.print_on_lcd(line_number, line)

    def _cleanse(self, new_lines: dict):
        return {
            line: value.strip()
            for line, value
            in new_lines.items()
        }


class HomeMode4x20:
    arrows = {
        'UP': 'U',
        'up': 'u',
        'DOWN': 'D',
        'down': 'd',
        'CONSTANT': '-',
        'both': '⇅'
        }
    parameter_string_lengths = {
        'illuminance': 3,
        'temperature': 4,
        'humidity': 3,
        'pressure': 4,
        'pressure_history': 8
    }
    preview = {
        #   12345678901234567890
        1: 'DD.MM.YYYY xxxxhPa ↑',
        2: 'DP:xx.xC xxxLX xx.x%',
        3: 'DZ:xx.xC    TP:xx.xC',
        4: 'D:-xx.xC            '
    }

    @property
    def template(self):
        return {
            'duzy pokoj': {
                'temperature': '--.--',
                'pressure': '----',
                'illuminance': '---',
                'humidity': '--.-'
            },
            'trzeci pokoj': {
                'temperature': '--.--',
                'pressure': '----'
            },
            'pokoj dziewczyn': {
                'temperature': '--.--'
            },
            'outdoors': {
                'temperature': '---.--'
            }
        }

    def get_required_tables(self) -> tuple[str]:
        return ('home_measures', 'illuminance')

    def build_lines(self, dataset: dict[dict], pressure_trend: str):
        date = datetime.date.today().isoformat().split('-')
        date_formatted = f'{date[2]}.{date[1]}.{date[0]}'
        trend = self.arrows[pressure_trend.upper()]
        self.set_formatting(dataset)
        return {
            1: f"{date_formatted} {dataset['trzeci pokoj']['pressure']}hPa {trend}",
            2: f"DP:{dataset['duzy pokoj']['temperature']}C {dataset['duzy pokoj']['illuminance']}lx {dataset['duzy pokoj']['humidity']}%",
            3: f"DZ:{dataset['pokoj dziewczyn']['temperature']}C    TP:{dataset['trzeci pokoj']['temperature']}C",
            4: f"D:{dataset['outdoors']['temperature']}C" + " " * 12
        }

    def set_formatting(self, dataset: dict[str]):
        if len(dataset['trzeci pokoj']['pressure']) == 3:
            dataset['trzeci pokoj']['pressure'] = ' ' + dataset['trzeci pokoj']['pressure']

        # TECHNICAL DEBT
        if dataset['duzy pokoj']['illuminance'] > '999':
            dataset['duzy pokoj']['illuminance'] = '999'
        else:
            if dataset['duzy pokoj']['illuminance'] == '---':
                dataset['duzy pokoj']['illuminance'] = '---.'
            else:
                dataset['duzy pokoj']['illuminance'] = str(float(dataset['duzy pokoj']['illuminance']))
            dataset['duzy pokoj']['illuminance'] = (
                ' '
                * (3 - len(dataset['duzy pokoj']['illuminance'].split('.')[0]))
                + dataset['duzy pokoj']['illuminance'].split('.')[0]
            )
            # END?

        dataset['outdoors']['temperature'] = (
            ' '
            * (6 - len(dataset['outdoors']['temperature']))
            + dataset['outdoors']['temperature']
        )[:-1]

        dataset['duzy pokoj']['temperature'] = dataset['duzy pokoj']['temperature'][:-1]
        dataset['pokoj dziewczyn']['temperature'] = dataset['pokoj dziewczyn']['temperature'][:-1]
        dataset['trzeci pokoj']['temperature'] = dataset['trzeci pokoj']['temperature'][:-1]


class EnchancedOutdoor4x20:
    arrows = {
        'UP': 'U',
        'up': 'u',
        'DOWN': 'D',
        'down': 'd',
        'CONSTANT': '-',
        'both': '⇅'
        }
    parameter_string_lengths = {
        'illuminance': 3,
        'temperature': 4,
        'humidity': 3,
        'pressure': 4,
        'pressure_history': 8
    }
    preview = {
        #   12345678901234567890
        1: r'DD.MM.YYYY xxxxhPa ↑',
        2: r'DP: xx.xC  |  -xx.xC',
        3: r'    xx.x%  |   xx.x%',
        4: r'DZ:-xx.xC  |  xxx lx'
    }

    @property
    def template(self):
        return {
            'duzy pokoj': {
                'temperature': '--.--',
                'humidity': '--.-'
            },
            'pokoj dziewczyn': {
                'temperature': '--.--'
            },
            'outdoors': {
                'temperature': '---.-',
                'pressure': '----',
                'humidity': '--.-',
                'illuminance': '---'
            }
        }

    def get_required_tables(self) -> tuple[str]:
        return ('home_measures', 'illuminance')

    def build_lines(self, dataset: dict[dict], pressure_trend: str):
        date = datetime.date.today().isoformat().split('-')
        date_formatted = f'{date[2]}.{date[1]}.{date[0]}'
        trend = self.arrows[pressure_trend]
        self.set_formatting(dataset)
        return {
            1: f"{date_formatted} {dataset['outdoors']['pressure']}hPa {trend}",
            2: f"DP: {dataset['duzy pokoj']['temperature']}C  |  {dataset['outdoors']['temperature']}C",
            3: f"    {dataset['duzy pokoj']['humidity']}C  |  {dataset['outdoors']['humidity']}%",
            4: f"DZ: {dataset['pokoj dziewczyn']['temperature']}C  |  {dataset['outdoors']['illuminance']} lx"
        }

    def set_formatting(self, dataset: dict[str]):
        if len(dataset['outdoors']['pressure']) == 3:
            dataset['outdoors']['pressure'] = ' ' + dataset['outdoors']['pressure']

        # TECHNICAL DEBT
        if dataset['outdoors']['illuminance'] > '999':
            dataset['outdoors']['illuminance'] = '999'
        else:
            if dataset['outdoors']['illuminance'] == '---':
                dataset['outdoors']['illuminance'] = '---.'
            else:
                dataset['outdoors']['illuminance'] = str(float(dataset['outdoors']['illuminance']))
            dataset['outdoors']['illuminance'] = (
                ' '
                * (3 - len(dataset['outdoors']['illuminance'].split('.')[0]))
                + dataset['outdoors']['illuminance'].split('.')[0]
            )
            # END?

        dataset['outdoors']['temperature'] = (
            ' '
            * (6 - len(dataset['outdoors']['temperature'][:-1]))
            + dataset['outdoors']['temperature']
        )[:-1]

        dataset['duzy pokoj']['temperature'] = dataset['duzy pokoj']['temperature'][:-1]
        dataset['pokoj dziewczyn']['temperature'] = dataset['pokoj dziewczyn']['temperature'][:-1]
