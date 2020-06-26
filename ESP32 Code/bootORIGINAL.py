import time
import array
from umqtt.simple import MQTTClient
import ubinascii
import machine
from machine import Pin
import micropython
import network
import esp

# wifi network credentials
ssid = 'ESPWIFI'
password = 'ESPWIFI12'
mqtt_server = '192.168.43.175'

# assigning what topic to subscribe to and publish to
topic_sub = b'motors'
client_id = 'ESP32'

# connects the esp 32 to the wifi network
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())


