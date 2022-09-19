from RPi_GPIO_i2c_LCD import lcd
from time import sleep
import datetime

menu = {'dashboard': (
            'Duzy pokoj: ',
            'Trzeci pokoj:',
            'IP ',
            'Status sprzetow:'
            )
        }


class LCD():
    def __init__(self, i2c_address=0x27):
        self.menu = menu
        self.display = lcd.HD44780(i2c_address)

    def show_menu(self, temperature, status, rpi_ip):
        self.display.clear()
        self.display.set(self.menu['dashboard'][0] + str(temperature[0])[:4] + 'C', 1)
        self.display.set(self.menu['dashboard'][1] + str(temperature[1])[:4] + 'C', 2)
        #self.display.set(self.menu['dashboard'][1] + str(rpi_ip), 2)
        self.display.set('Tata Mama iPad Inter', 3)
        self.display.set(f' {status["karol"]}    {status["aga"]}    {status["iPad"]}    {status["internet"]}', 4)
        print('10-4, menu on LCD')
        return True

    def clear(self):
        self.display.clear()
        print('LCD Display cleared')

    def update_temp(self, temperature: list):
        self.display.set(self.menu['dashboard'][0] + str(temperature[0])[:4] + 'C', 1)
        self.display.set(self.menu['dashboard'][1] + str(temperature[1])[:4] + 'C', 2)

    def update_status(self, server):
        statuses = server
        self.display.set(f' {statuses["karol"]}    {statuses["aga"]}    {statuses["iPad"]}    {statuses["internet"]}', 4)
    
    def update_all(self, temperature, servers):
        self.update_status(servers)
        self.update_temp(temperature)

    def backlight_off(self):
        self.display.backlight('off')

    def backlight_on(self):
        self.display.backlight('on')
    
    def write(self, text, line=None, clear=False):
        print(f'Write line - {line} - {datetime.datetime.now()}')
        text_to_display = ()
        counter = 4
        text = str(text)
        if line is None:
            while len(text) > 0  or counter > 0:
                print(len(text))
                print(type(len(text)))
                if len(text) > 20:
                    counter -= 1
                    print('While loop in write()')
                    text_to_display = text_to_display + (text[:20], )
                    text = text[20:]
                elif len(text) == 0:
                    break
                else:
                    print('While loop in write() else')
                    text_to_display = text_to_display + (text, )
                    text = '' 
            if clear:
                self.clear()
            for i in range(1,len(text_to_display)):
                print('for loop after write() while loop')
                self.display.set(text_to_display[i], i)
        else:
            self.display.set(text, line)
    
    def task_done(self):
        self.display.set('                    ', 1)
        self.display.set('        DONE        ', 2)
        self.display.set('                    ', 3)
        self.display.set('                    ', 4)
        
    def clear_line(self, line_number):
        if line_number > 4 or line_number < 1:
            print('Line number wrong: ', line_number)
            return None
        self.display.set('                    ', line_number)
