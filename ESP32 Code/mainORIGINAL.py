forward = Pin(14, Pin.OUT)
left = Pin(12, Pin.OUT)
back = Pin(15, Pin.OUT)
right = Pin(13, Pin.OUT)
m_decode = 'none'
trash = 'none'
dir_decode = 'none'
dir_decode2 = 'none'
r_decode = 'none'
r_decode2 = 'none' 
f=0
l=0
b=0
r=0
dir=0
range=0
dir1 =0
range1=0

#this is the callback function, meaning when the server is updated, this function is automatically called to read the new data

def sub_cb(topic_sub, msg):
 #this code will take in the message from the server and decode it from a string into two integers
 #the integers are the direction and range sent from the tracking program
 m_decode= msg
 dir_decode = m_decode.decode('ignore')
 dir1, range1 = dir_decode.split(',')
 dir = int(dir1)
 range = int(range1)
 #if the direction is not 0, then the motor associated with that direction will be turned on
 # dir = 1 is forward
 # dir = 2 is left
 # dir = 3 is right
 # dir = 4 is back

 #if the range is between 0 and 6, the motors will be turned on to the lowest vibration
 if 0<range<6:
   if dir == 1:
      f = 1
      l = 0
      r = 0
      b = 0
   elif dir == 2:
      f = 0
      l = 1
      r = 0
      b = 0
   elif dir == 3:
      f = 0
      l = 0
      r = 1
      b = 0
   elif dir == 4:
      f = 0
      l = 0
      r = 0
      b = 1
 elif 6<= range < 20:
   if dir == 1:
      f = 2
      l = 0
      r = 0
      b = 0
   elif dir == 2:
      f = 0
      l = 2
      r = 0
      b = 0
   elif dir == 3:
      f = 0
      l = 0
      r = 2
      b = 0
   elif dir == 4:
      f = 0
      l = 0
      r = 0
      b = 2
 elif 20 <= range:
   if dir == 1:
      f = 3
      l = 0
      r = 0
      b = 0
   elif dir == 2:
      f = 0
      l = 3
      r = 0
      b = 0
   elif dir == 3:
      f = 0
      l = 0
      r = 3
      b = 0
   elif dir == 4:
      f = 0
      l = 0
      r = 0
      b = 3
 else:
   f = 0
   l = 0
   r = 0
   b = 0
  
 #here is where the values of the motors are set
 forward.value(f)
 left.value(l)
 back.value(b)
 right.value(r)
 
 

#this function connects to the web server and subscribes to the topic that the tracking software sends the data

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(2)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    
  except OSError as e:
    restart_and_reconnect()

    
