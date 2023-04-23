import threading
import queue
import datetime
from time import sleep
from dataclasses import dataclass
from pytz import timezone

from flask import Flask
from RPi_GPIO_i2c_LCD import lcd as GPIO_LCD
from psycopg2 import OperationalError
#from tests.test_GPIO.stub import lcd_stub as GPIO_LCD

from GPIO.lcdprinter import LCDPrinter, HomeMode4x20
from GPIO.bh1750_zero import BH1750
from GPIO.bme280_zero import BME280_zero
from database.dbquery import Query
from database.postgresdriver import pgDriver

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


app = Flask(__name__)

RUNNING = 1
STOPPED = 0

LCD_CONTROLLER_THREAD_STATUS = -1


@dataclass
class DataQueue:
    create_queue: queue.Queue = queue.Queue(maxsize=0)
    read_queue: queue.Queue = queue.Queue(maxsize=0)


class DBController(threading.Thread):

    querymaker = Query(pgDriver, 'home')
    name = 'DBController'

    def run(self):

        post_data = None

        while True:
            # Technical DEBT
            try:
                if DataQueue.read_queue.empty():
                    dataset, pressure_trend = self.get_lcd_dataset()
                    self.send_lcd_dataset(dataset, pressure_trend)
                if DataQueue.create_queue.qsize() > 0:
                    post_data = DataQueue.create_queue.get()
                    self.querymaker.insert_sensor_data(
                        (post_data,)
                    )
                sleep(2)
            except OperationalError as exc:
                if post_data:
                    DataQueue.create_queue.put_nowait(post_data)
                print(exc.args)
                sleep(20)
            # END

    def get_lcd_dataset(self):
        dataset = self.querymaker.get_transformed_latest(
            LCDController().get_tables(),
            LCDController().get_template()
        )
        pressure_trend = self.querymaker.get_pressure_trend()
        return (dataset, pressure_trend)

    def send_lcd_dataset(self, dataset: list, pressure_trend: tuple[list]) -> None:
        DataQueue.read_queue.put_nowait((dataset, pressure_trend))


class LCDController(threading.Thread):
    """
    CHANGE THE lcd_stub BEROFE MIGRATING TO RASPBERRY`
    """
    printer = LCDPrinter(GPIO_LCD.HD44780(0x27))
    name = 'LCDController'

    def run(self):
        global LCD_CONTROLLER_THREAD_STATUS
        LCD_CONTROLLER_THREAD_STATUS = RUNNING
        self.startup()

        while LCD_CONTROLLER_THREAD_STATUS == RUNNING:
            most_recent_data_by_rooms, pressure_trend = DataQueue.read_queue.get()
            lines = self.get_mode().build_lines(
                most_recent_data_by_rooms,
                # Technical DEBT
                pressure_trend
                if pressure_trend
                else 'CONSTANT')
                # END
            if lines != self.printer.get_lines():
                self.printer.set_lines(lines)
            sleep(15)

    def startup(self):
        self.printer.set_lines({
            #   12345678901234567890
            1: 'Initializing...     ',
            2: ' ' * 20,
            3: ' ' * 20,
            4: ' ' * 20
        })

    def get_tables(self):
        return self.get_mode().get_required_tables()

    def get_mode(self):
        return HomeMode4x20()

    @classmethod
    def get_template(cls):
        return cls.get_mode(cls).template


class BME280Controller(threading.Thread):

    bus = SMBus(1)
    bme280 = BME280_zero(i2c_dev=bus)
    name = 'BME280Controller'

    def run(self):
        while True:
            temperature = self.bme280.get_temperature()
            pressure = self.bme280.get_pressure()
            humidity = self.bme280.get_humidity()
            sea_level_pressure = self.bme280.get_sea_level_pressure(
                pressure, temperature
            )
            DataQueue.create_queue.put_nowait(
                {
                    'home_measures': {
                        'ts_id': get_ts_id(),
                        'room': '\'outdoors\'',
                        'temperature': temperature,
                        'pressure': sea_level_pressure,
                        'humidity': humidity
                    }
                }
            )
            sleep(58.5)


class BH1750Controller(threading.Thread):

    bus = SMBus(1)
    sensor = BH1750(bus)
    name = 'BH1750Controller'

    def run(self):
        while True:
            try:
                illuminance = self.sensor.get_illuminance()

                DataQueue.create_queue.put_nowait(
                    {
                        'home_measures': {
                            'ts_id': get_ts_id(),
                            'room': '\'outdoors\'',
                            'illuminance': illuminance
                        }
                    }
                )
            except Exception:
                pass
            finally:
                sleep(58.5)


class ThreadWatcher(threading.Thread):
    THREAD_NAMES = {
        'BH1750Controller': BH1750Controller,
        'BME280Controller': BME280Controller,
        'LCDController': LCDController,
        'DBController': DBController
    }

    def run(self):
        while True:
            self.revive_dead_threads()
            sleep(300)

    def revive_dead_threads(self):
        alive_threads = tuple(threading.enumerate())
        for thread in self.THREAD_NAMES:
            if not self._is_alive(thread, alive_threads):
                self.revive_thread(thread)

    def _is_alive(self, thread: str, alive_threads: tuple):
        return thread in alive_threads

    def revive_thread(self, thread: str):
        self.THREAD_NAMES[thread]().start()


def get_ts_id():
    return f"'{datetime.datetime.now().astimezone(timezone('Europe/Berlin'))}'"


@app.route("/duzy_pokoj/<temperature>/<humidity>/<pressure>", methods=['GET'])
def duzy_pokoj(temperature, humidity, pressure):
    DataQueue.create_queue.put_nowait(
        {
            'home_measures': {
                'ts_id': get_ts_id(),
                'room': '\'duzy pokoj\'',
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure
            }
        }
    )
    return 'OK'


@app.route("/duzy_pokoj/luxmeter/<illuminance>", methods=['GET'])
def duzy_pokoj_luxmeter(illuminance):
    DataQueue.create_queue.put_nowait(
        {
            'illuminance': {
                'ts_id': get_ts_id(),
                'room': '\'duzy pokoj\'',
                'illuminance': illuminance
            }
        }
    )
    return 'OK'


@app.route("/pokoj_dziewczyn/temperature/<data>", methods=['GET'])
def pokoj_dziewczyn(data):
    DataQueue.create_queue.put_nowait(
        {
            'home_measures': {
                'ts_id': get_ts_id(),
                'room': '\'pokoj dziewczyn\'',
                'temperature': data
            }
        }
    )
    return 'OK'


@app.route("/threads", methods=['GET'])
def threads():
    return str([x.getName() for x in threading.enumerate()])


if __name__ == 'app':
    DBController().start()
    LCDController().start()
    BME280Controller().start()
    BH1750Controller().start()
