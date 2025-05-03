import time
import board
import busio
import adafruit_dht
import RPi.GPIO as GPIO
from digitalio import DigitalInOut, Direction
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

import firebase_admin
from firebase_admin import credentials, db

# ------------------ FIREBASE SETUP ------------------
cred = credentials.Certificate("/home/rasp/firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project-id.firebaseio.com/'
})
ref = db.reference('air_monitor')

# ------------------ DHT22 SETUP ------------------
dht_sensor = adafruit_dht.DHT22(board.D4)

# ------------------ MQ135 SETUP ------------------
mq135_pin = 17  # BCM pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(mq135_pin, GPIO.IN)

# ------------------ OLED SETUP ------------------
i2c = busio.I2C(board.D3, board.D2)  # GPIO 3 (SCL), GPIO 2 (SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)
oled.show()

image = Image.new("1", (128, 64))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# ------------------ MAIN LOOP ------------------
try:
    while True:
        try:
            temperature_c = dht_sensor.temperature
            humidity = dht_sensor.humidity
            air_quality = GPIO.input(mq135_pin)
            air_status = "Good" if air_quality == 1 else "Poor"

            print(f"Temp: {temperature_c:.1f}°C | Humidity: {humidity:.1f}% | Air: {air_status}")

            # OLED display
            draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
            draw.text((0, 0), f"Temp: {temperature_c:.1f} C", font=font, fill=255)
            draw.text((0, 16), f"Humidity: {humidity:.1f} %", font=font, fill=255)
            draw.text((0, 32), f"Air Quality: {air_status}", font=font, fill=255)
            oled.image(image)
            oled.show()

            # Upload to Firebase
            ref.set({
                'temperature_c': temperature_c,
                'humidity': humidity,
                'air_quality': air_status,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            })

        except RuntimeError as e:
            print("Sensor error:", e.args[0])
        except Exception as e:
            dht_sensor.exit()
            raise e

        time.sleep(3)

except KeyboardInterrupt:
    print("Program stopped.")

finally:
    dht_sensor.exit()
    GPIO.cleanup()
