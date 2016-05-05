import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD
from pylms import server
from erres_variables import *
from eplib_hardware import *
from eplib_interface import *
import time
from unidecode import *

# region Hardware configuration
GPIO.setmode(GPIO.BCM)
buttons = (RE1B, RE2B, RE3B)
GPIO.setup(buttons, GPIO.IN, pull_up_down=GPIO.PUD_UP)
RE1 = RotaryEncoder.Worker(RE1L, RE1R)
RE2 = RotaryEncoder.Worker(RE2L, RE2R)
RE3 = RotaryEncoder.Worker(RE3L, RE3R)
RE1.start()
RE2.start()
RE3.start()
lcd_rs = 27
lcd_en = 22
lcd_d4 = 25
lcd_d5 = 24
lcd_d6 = 23
lcd_d7 = 18
lcd_red   = 4
lcd_green = 17
lcd_blue  = 7
lcd_columns = 20
lcd_rows    = 4
lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,lcd_columns, lcd_rows, lcd_red, lcd_green, lcd_blue, enable_pwm=True)
lcd.set_color(LCD_red, LCD_green, LCD_blue)
line1 = 0
line2 = 1
line3 = 2
line4 = 3
lcd.clear()
# endregion hardware configuration


# region Utility functions
def status_update(str1, str2=None):
    lcd.message(str1)
    if str2 is None:
        print(str1,)
    else:
        print(str2,)
# endregion

# region LMS configuration and initialization
print("Initializing Erres Interface v0.3")
init = True
numberOfTries = 0
status_update("Verbinden")
timeElapsedBetweenTries = 0
while init:
    try:
        numberOfTries += 1
        timeElapsedBetweenTries = pauseBetweenRetries
        s = server.Server(lms_server)
        s.connect()
        init = False
    except:
        status_update(".")
        while timeElapsedBetweenTries > 0:
            if numberOfTries > retriesBeforeFailure:
                status_update("No server error","No server found. Quitting.")
                exit()
            print("Server not ready. Trying again in %d seconds" % timeElapsedBetweenTries)
            time.sleep(1)
            timeElapsedBetweenTries -= 1
lcd.message("\n")
init = True
numberOfTries = 0
status_update(lms_player)
while init:
    try:
        numberOfTries += 1
        timeElapsedBetweenTries = pauseBetweenRetries
        p = s.get_player(lms_player)
        init = False
    except:
        lcd.message(".")
        while timeElapsedBetweenTries > 0:
            if numberOfTries > retriesBeforeFailure:
                status_update("No player error","No player found. Quitting.")
                exit()
            print("Player not ready. Trying again in %d seconds" % timeElapsedBetweenTries)
            time.sleep(1)
            timeElapsedBetweenTries -= 1
lcd.message("\n")
print("Initialization complete")
# endregion



ui = interface(lcd, p, s, 2)
ui.import_favorites(favoritesFile)
ui.clear()
ui.redraw()

displayUpdateCycleCounter = displayUpdateCycles

while True:
    # Get all inputs
    RE1_delta = RE1.get_delta()
    RE2_delta = RE2.get_delta()
    RE3_delta = RE3.get_delta()
    RE1_press = not(GPIO.input(RE1B))
    RE2_press = not(GPIO.input(RE2B))
    RE3_press = not(GPIO.input(RE3B))

    # Button behavior
    if RE1_press:
        ui.RE1_press()
    if RE1_delta != 0:
        ui.RE1_turn(RE1_delta)
    if RE2_press:
        ui.RE2_press()
    if RE2_delta != 0:
        ui.RE2_turn(RE2_delta)
    if RE3_press:
        pass
    if RE3_delta != 0:
        ui.RE3_turn(RE3_delta)

    displayUpdateCycleCounter -= 1
    if displayUpdateCycleCounter == 0:
        ui.redraw()
        displayUpdateCycleCounter = displayUpdateCycles

