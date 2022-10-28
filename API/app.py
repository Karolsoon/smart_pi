import threading
import queue
import datetime
from time import sleep
from dataclasses import dataclass
from pytz import timezone


#from RPi_GPIO_i2c_LCD import lcd as GPIO_LCD
from tests.test_GPIO.stub import lcd_stub as GPIO_LCD

from GPIO.lcdprinter import LCDPrinter, HomeMode4x20
from GPIO.bmp280_zero import BMP280_zero
from database.dbquery import Query
from database.postgresdriver import pgDriver

RUNNING = 1
STOPPED = 0

LCD_CONTROLLER_THREAD_STATUS = -1


@dataclass
class DataQueue:
    create_queue: queue.Queue(maxsize=0)
    read_queue: queue.Queue(maxsize=0)


class DBController(threading.Thread):
    
    querymaker = Query(pgDriver, 'home')
    
    def run(self):
        pass

    def get_lcd_dataset(self):
        pass

    def send_to_lcd(self, dataset: list) -> None:
        pass


class LCDController(threading.Thread):
    """
    CHANGE THE lcd_stub BEROFE MIGRATING TO RASPBERRY`
    """
    printer = LCDPrinter(GPIO_LCD)
    querymaker = Query(pgDriver, 'home')
    mode = HomeMode4x20

    def run(self):
        global LCD_CONTROLLER_THREAD_STATUS
        LCD_CONTROLLER_THREAD_STATUS = RUNNING
        self.startup()

        while LCD_CONTROLLER_THREAD_STATUS == RUNNING:
            most_recent_data_by_rooms = self.querymaker.get_transformed_latest(
                                                self.mode.get_required_tables()
            )
            lines = self.mode.build_lines(
                most_recent_data_by_rooms,
                self.querymaker.get_pressure_trend)
            self.printer.set_lines(lines)
            sleep(15)

    def startup(self):
        self.printer.set_lines({
            #   12345678901234567890
            1: 'Initialising...     ',
            2: ' ' * 20,
            3: ' ' * 20,
            4: ' ' * 20
        })


def get_ts_id():
    return datetime.datetime.now().astimezone(timezone('Europe/Berlin'))


#@app.route("/duzy_pokoj/<temperature>/<humidity>/<pressure>", methods=['GET'])
def duzy_pokoj(temperature, humidity, pressure):
    DataQueue.create_queue.put_nowait(
        {
            'home_measures': {
                'ts_id': get_ts_id(),
                'room': 'duzy pokoj',
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure
            }
        },
    )
    return 'OK'


#@app.route("/duzy_pokoj/luxmeter/<illuminance>", methods=['GET'])
def duzy_pokoj_luxmeter(illuminance):
    DataQueue.create_queue.put_nowait(
        {
            'illuminance': {
                'ts_id': get_ts_id(),
                'room': 'duzy pokoj',
                'illuminance': illuminance
            }
        }
    )
    return 'OK'


#@app.route("/pokoj_dziewczyn/temperature/<data>", methods=['GET'])
def pokoj_dziewczyn(data):
    DataQueue.create_queue.put_nowait(
        {
            'home_measures': {
                'ts_id': get_ts_id(),
                'room': 'pokoj dziewczyn',
                'temperature': data
            }
        }
    )
    return 'OK'


#@app.route("/threads", methods=['GET'])
def threads():
    return str([x.getName() for x in threading.enumerate()])


if __name__ == '__main__':
    pass
