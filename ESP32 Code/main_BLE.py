import bluetooth
import time
import machine
from machine import Pin
from bleuart import BLEUART

# Forward motor pin B, PWMB, pin 4
# Left motor pin A, PWMA, pin 34
# Back motor pin B, PWMB, pin 35
# Right motor pin A, PWMA, pin 2
motor1 = machine.PWM(Pin(4))
motor2 = machine.PWM(Pin(32))
motor3 = machine.PWM(Pin(33))
motor4 = machine.PWM(Pin(2))

motor1.freq(1000)
motor2.freq(1000)
motor3.freq(1000)
motor4.freq(1000)

motor1.duty(0)
motor2.duty(0)
motor3.duty(0)
motor4.duty(0)

forward = 0
left = 0
back = 0
right = 0

def start_sleeve():
    ble = bluetooth.BLE()
    uart = BLEUART(ble)
 
    def set_PWM():
      # Read and decode data sent over BLE UART
      rx_payload = uart.read().decode().strip()
      
      # Split the formatted payload for direction and range
      # Assumes that sent messages are formatted properly & non-empty
      direction, range = rx_payload.split(',')
      direction = int(direction)
      range = int(range)
      
      # Range comes in 0, 1, 2, 3
      # Duty is 1/3 of the max, ie. 33.33%, 66.33%, 100%
      # Max for PWM is 1023, 341 is 1/3 *1023
      duty = int(range*341)
      
      # Assign duty based on direction
      if direction == 1:
        forward = duty
        left = 0
        back = 0
        right = 0
      elif direction == 2:
        forward = 0
        left = duty
        back = 0
        right = 0
      elif direction == 3:
        forward = 0
        left = 0
        back = duty
        right = 0
      elif direction == 4:
        forward = 0
        left = 0
        back = 0
        right = duty
      else: # Set all to 0
        forward = 0
        left = 0
        back = 0
        right = 0
      
      # Set duty
      motor1.duty(forward)
      motor2.duty(left)
      motor3.duty(back)
      motor4.duty(right)
    
    # Set callback for BLE event
    # Callbacks triggered immediately when new payload received
    uart.irq(handler = set_PWM)

    try:
      while True: # Infinite loop, sleep used as a placeholder
        time.sleep_ms(1)
    except KeyboardInterrupt:
      pass

    # Close the BLE UART connection
    uart.close()

if __name__ == "__main__":
    start_sleeve()


    
