# Forward motor pin B, PWMB, pin 4
# Left motor pin A, PWMA, pin 34
# Back motor pin B, PWMB, pin 35
# Right motor pin A, PWMA, pin 2
motor1 = machine.PWM(Pin(4))
motor2 = machine.PWM(Pin(32))
motor3 = machine.PWM(Pin(33))
motor4 = machine.PWM(Pin(2))

# Set motor frequencies
motor1.freq(1000)
motor2.freq(1000)
motor3.freq(1000)
motor4.freq(1000)

# Initialize motor duties
motor1.duty(0)
motor2.duty(0)
motor3.duty(0)
motor4.duty(0)

# Initialize direction variables
forward = 0
left = 0
back = 0
right = 0

# Declare event codes
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

# org.bluetooth.characteristic.gap.appearance.xml
# Declare appearance as a generic computer
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)

# Declare advertising codes
_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_APPEARANCE = const(0x19)

# Set UUIDs & declare UART service
_UART_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY,)
_UART_RX = (ubluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), ubluetooth.FLAG_WRITE,)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX,),)


# Generate a payload to be passed to gap_advertise(adv_data=...)
def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
  payload = bytearray()

  def _append(adv_type, value):
    nonlocal payload
    payload += struct.pack("BB", len(value) + 1, adv_type) + value

  _append(
    _ADV_TYPE_FLAGS,
    struct.pack("B", (0x01 if limited_disc else 0x02) + (0x00 if br_edr else 0x04)),
  )

  if name:
    _append(_ADV_TYPE_NAME, name)

  if services:
    for uuid in services:
      b = bytes(uuid)
      if len(b) == 2:
        _append(_ADV_TYPE_UUID16_COMPLETE, b)
      elif len(b) == 4:
        _append(_ADV_TYPE_UUID32_COMPLETE, b)
      elif len(b) == 16:
        _append(_ADV_TYPE_UUID128_COMPLETE, b)

  # See org.bluetooth.characteristic.gap.appearance.xml
  _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

  return payload
  
  
# UART over BLE class
class BLEUART:
  def __init__(self, ble, name="Haptic Sleeve", rxbuf=100):
    self._ble = ble
    #self._ble.active(True)
    self._ble.irq(handler=self._irq)
    ((self._tx_handle, self._rx_handle,),) = self._ble.gatts_register_services((_UART_SERVICE,))
    
    # Increase the size of the rx buffer and enable append mode.
    self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
    self._connections = set()
    self._rx_buffer = bytearray()
    self._handler = None
    # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
    self._payload = advertising_payload(name=name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
    self._advertise()

  def irq(self, handler):
    self._handler = handler

  def _irq(self, event, data):
    # Track connections so we can send notifications.
    if event == _IRQ_CENTRAL_CONNECT:
      conn_handle, addr_type, addr, = data
      self._connections.add(conn_handle)
    elif event == _IRQ_CENTRAL_DISCONNECT:
      conn_handle, addr_type, addr, = data
      if conn_handle in self._connections:
        self._connections.remove(conn_handle)
      # Start advertising again to allow a new connection.
      self._advertise()
    elif event == _IRQ_GATTS_WRITE:
      conn_handle, value_handle, = data
      if conn_handle in self._connections and value_handle == self._rx_handle:
        self._rx_buffer += self._ble.gatts_read(self._rx_handle)
        if self._handler:
          self._handler()

  def any(self):
    return len(self._rx_buffer)

  def read(self, sz=None):
    if not sz:
      sz = len(self._rx_buffer)
    result = self._rx_buffer[0:sz]
    self._rx_buffer = self._rx_buffer[sz:]
    return result

  def write(self, data):
    for conn_handle in self._connections:
      self._ble.gatts_notify(conn_handle, self._tx_handle, data)

  def close(self):
    for conn_handle in self._connections:
      self._ble.gap_disconnect(conn_handle)
    self._connections.clear()

  def _advertise(self, interval_us=500000):
    self._ble.gap_advertise(interval_us, adv_data=self._payload)


# Function to start the main sleeve code
def start_sleeve():  
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
  uart = BLEUART(ble)
  uart.irq(handler = set_PWM)

  try:
    while True: # Infinite loop, sleep used as a placeholder
      time.sleep_ms(1)
  except KeyboardInterrupt as e:
    print(e)
    pass

  # Close the BLE UART connection
  uart.close()
  
  
if __name__ == "__main__":
  start_sleeve()
