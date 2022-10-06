import datetime
import threading
import subprocess
import psycopg2
from math import sin
from time import sleep
from bmp280 import BMP280

from flask import Flask
from db_con import Connector
from LCD import LCD


DATA_TYPES = ('temperature', 'pressure', 'humidity')
SCHEMA = 'home'
TRZECI_POKOJ_THREAD = 'trzeci_pokoj_thread'
LCD_THREAD = 'lcd_thread'


app = Flask(__name__)
lcd = LCD()
db = Connector(SCHEMA)

# Thead lock
lock = threading.Lock()


def convert_temp(temperature, room):
    """
    Converts the received temperature into float data type.
    Writes to log file on failure.

    Returns adequate response on success or failure.
    """
    try:
        temperature = float(temperature)

        return (temperature, "Received. OK.")
    except TypeError:
        with open('log.txt', mode='ta') as logfile:
            logfile.write(f'{datetime.datetime.now()} - {room} - Received wrong temperature format')
            return (None, "Received wrong format")

# def convert_c_to_k(temperature_c):
#     """
#     Converts temperature in celsius to kelvin
#     """
#     return temperature_c + 273.15

# def convert_to_sea_level(atmospheric_pressure_hpa, temperature_c):
#     """
#     Calculates the sea_level_pressure based on the 
#     atmospheric pressure and temperature measurements
#     """
#     # Declare constant values for my location
#     altitude = wysokosc = 100
#     latitude = szer_geo = 51.659167
#     gas_constant = stala_gazowa = 8.31446261815324
#     air_molar_mass = masa_molowa_powietrza = 0.0289644
#     atmospheric_pressure_bar = atmospheric_pressure_hpa / 1000

#     # Calculate and/or convert values
#     temperature_k = convert_c_to_k(temperature_c)
#     gravitational_acceleration = 9.780318 * (1 + (0.0053024 * sin(latitude) ** 2) - \
#         (0.0000058 * sin(2 * latitude) ** 2) - 3.086 * 10 ** (-6) * altitude)

#     # Calculate the sea_level_pressure
#     sea_level_pressure = atmospheric_pressure_bar / (1 \
#             - (air_molar_mass * gravitational_acceleration * altitude) \
#                 / (gas_constant * temperature_k))

#     sea_level_pressure_hpa = sea_level_pressure * 1000
#     print(f'Sea level: {sea_level_pressure_hpa} \n Pressure: {atmospheric_pressure_hpa}')

#     return round(sea_level_pressure_hpa, 0)

def trzeci_pokoj():
    """
    Is a local BMP280 temperature and pressure sensor attached to the Pi Zero 
    central/collector node.

    Gets the current readings and inserts into the PostgreSQL db.
    """
    try:
        from smbus2 import SMBus
    except ImportError:
        from smbus import SMBus

    bus = SMBus(1)
    bmp280 = BMP280(i2c_dev=bus)

    while True:
        temperature = bmp280.get_temperature()
        pressure = bmp280.get_pressure()
        sea_level_pressure = convert_to_sea_level(pressure, temperature)

        try:
            with lock:
                with Connector('home') as db:
                    db.insert_data('Trzeci pokoj', (temperature, sea_level_pressure, 'NULL'))
        except psycopg2.OperationalError:
            print(f'{datetime.datetime.now()} - psycopg2.OperationalError - Server unavailable')
        finally:
            sleep(52)


def cirlicirli():
    """ Displays current temperatures of the rooms on the 4x20 LCD """
    while True:
        try:
            with lock:
                with Connector('home') as db:
                    duzy_pokoj_t = db.retrieve_data('temperature', 'duzy pokoj')
                    pokoj_dziewczyn_t = db.retrieve_data('temperature', 'pokoj dziewczyn')
                    trzeci_pokoj_t = db.retrieve_data('temperature', 'trzeci pokoj')
                    trzeci_pokoj_p = db.retrieve_data('pressure', 'trzeci pokoj')
                    lux = db.retrieve_data('illuminance', 'duzy pokoj', table='illuminance')
        except psycopg2.OperationalError:
            print(f'{datetime.datetime.now()} - psycopg2.OperationalError - Server unavailable')
            duzy_pokoj_t = pokoj_dziewczyn_t = trzeci_pokoj_t = trzeci_pokoj_p = '----'

        # Clear the LCD screen
        lcd.clear()

        if len(str(lux)) > 6:
            lux = 9999
        else:
            lux = str(lux).split('.')[0]
            lux = (4 - len(lux)) * ' ' + lux


        # Now write the gathered data on the LCD
        lcd.write(f'Duzy pokoj: {duzy_pokoj_t} C', 1)
        lcd.write(f'Pok.dziew : {pokoj_dziewczyn_t} C', 2)
        lcd.write(f'Trz.pokoj : {trzeci_pokoj_t} C', 3)
        lcd.write(f'Cisnienie : {trzeci_pokoj_p} hPa', 4)
        sleep(15)
        lcd.write(f'Lux       : {lux} lx ', 4)
        sleep(15)


@app.route("/")
def hello_world():
    """
    Sanity check if the server is running.
    """
    return "RPi server works"

@app.route("/start_biuro")
def start_biuro():
    """
    API endpoint for pokoj starting the sensor loop for BMP280.

    Returns a simple text response.
    """
    if 'trzeci_pokoj_thread' in [x.getName() for x in threading.enumerate()]:
        return '<p>Trzeci pokoj thread is already running</p>'

    trzeci_pokoj_thread = threading.Thread(target=trzeci_pokoj, args=(), daemon=True, name=TRZECI_POKOJ_THREAD)
    trzeci_pokoj_thread.start()
    return "Running measures in trzeci pokoj"

@app.route("/duzy_pokoj/<temperature>", methods=['GET'])
def duzy_pokoj(temperature):
    """
    API endpoint for duzy pokoj temperature sensor.
    Inserts the retrieved measurements into the DB.

    Returns success message or None.
    """
    room = 'Duzy pokoj'
    converted_temp, response = convert_temp(temperature, room)
    if converted_temp:
        with lock:
            with Connector('home') as db:
                db.insert_data(room, (converted_temp, 'NULL', 'NULL'))
    return response


@app.route("/duzy_pokoj/luxmeter/<illuminance>", methods=['GET'])
def duzy_pokoj_luxmeter(illuminance):
    """
    API endpoint for duzy pokoj luxmeter.
    Inserts the retrieved measurements into the DB.

    Returns success message or None.
    """
    room = 'Duzy pokoj'
    try:
        with lock:
            with Connector('home') as db:
                db.insert_lux_data(room, illuminance)
        response = 'OK'
    except psycopg2.OperationalError:
        print(f'{datetime.datetime.now()} - psycopg2.OperationalError - Server unavailable')
        response = 'OperationalError'
    return response


@app.route("/pokoj_dziewczyn/temperature/<data>", methods=['GET'])
def pokoj_dziewczyn(data):
    """
    API endpoint for pokoj dziewczyn temperature sensor.
    Inserts the retrieved measurements into the DB.

    Returns success message or None.
    """
    room = 'Pokoj dziewczyn'
    converted_temp, response = convert_temp(data, room)
    if converted_temp:
        with lock:
            with Connector('home') as db:
                db.insert_data(room, (converted_temp, 'NULL', 'NULL'))
    return response


@app.route("/pip/<person>/<is_light>", methods=['GET'])
def pip(person, is_light):
    """
    API endpoint for pip data.
    Inserts the retrieved measurements into the DB.
    """
    with lock:
        with Connector('home') as db:
            db.insert_pip_data(person, is_light)
    return 'Received pip. OK.'


@app.route("/start_lcd", methods=['GET'])
def lcd_start():
    """
    Starts the LCD thread.
    If the thread is already running does nothing.

    Returns a simple text response.
    """
    if LCD_THREAD in [x.getName() for x in threading.enumerate()]:
        return '<p>start_lcd already running</p>'

    lcd_thread = threading.Thread(target=cirlicirli, args=(), daemon=True, name=LCD_THREAD)
    lcd_thread.start()
    return '<p>Started start_lcd</p>'

@app.route("/zona/<data>", methods=['GET'])
def zona(data):
    """
    Writes the lines from the url onto the LCD
    Breaks line occording to the LCD line lenght

    Requires to use "." (dot) as the delimiter
    """
    # Clear the LCD to remove previous message 
    lcd.clear()

    data = data.replace('.', ' ')
    response = data
    msg = []
    while len(data) != 0:
        msg.append(data[:19])
        data = data[19:]

    i = 1
    while len(msg) > 0:
        lcd.write(msg.pop(0), i)
        i += 1
        if i == 4:
            sleep(5)
            i = 1
            lcd.clear()
    return response

@app.route("/threads", methods=['GET'])
def threads():
    return str([x.getName() for x in threading.enumerate()])


if __name__ == 'app':
    lcd.clear()
    trzeci_pokoj_thread = threading.Thread(target=trzeci_pokoj, args=(), daemon=True, name=TRZECI_POKOJ_THREAD)
    lcd_thread = threading.Thread(target=cirlicirli, args=(), daemon=True, name=LCD_THREAD)
    trzeci_pokoj_thread.start()
    sleep(0.3)
    lcd_thread.start()
