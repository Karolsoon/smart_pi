import threading

from GPIO.lcdprinter import LCDPrinter
from GPIO.bmp280_zero import BMP280_zero


#@app.route("/threads", methods=['GET'])
def threads():
    return str([x.getName() for x in threading.enumerate()])


#@app.route("/zona/<data>", methods=['GET'])
def zona(data):
    """
    Writes the lines from the url onto the LCD
    Breaks line occording to the LCD line lenght

    Requires to use "." (dot) as the delimiter
    """
    pass
    # Clear the LCD to remove previous message 
    # lcd.clear()

    # data = data.replace('.', ' ')
    # response = data
    # msg = []
    # while len(data) != 0:
    #     msg.append(data[:19])
    #     data = data[19:]

    # i = 1
    # while len(msg) > 0:
    #     lcd.write(msg.pop(0), i)
    #     i += 1
    #     if i == 4:
    #         sleep(5)
    #         i = 1
    #         lcd.clear()
    # return response


