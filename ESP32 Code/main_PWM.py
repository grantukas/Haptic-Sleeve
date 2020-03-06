
Pf = PWM(Pin(14))
Pl = PWM(Pin(12))
Pb = PWM(Pin(15))
Pr = PWM(Pin(13))

Pf.freq(1000) #freq of 1kHz was chosen because it feels right with the motors.
Pl.freq(1000)
Pb.freq(1000)
Pr.freq(1000)
m_decode = 'none'
trash = 'no'
dir_decode='no'
dir_decode2='no'
r_decode='no'
r_decode2='no'
f=0
l=0
b=0
r=0
dir=0
range=0
dir1=0
range1=0

def sub_cb(topic_sub, msg):
	m_decode = msg
	dir_decode = m_decode.decode('ignore')
	dir1, range1 = dir_decode.split(',')
	range = int(range1) # range comes in 1, 2, or 3
	dir = int(dir1)
	pulse = int(range*341) # pulse is 1/3 of the max, ie. 33.33%, 66.33%, 100%
						   # max for PWM is 1023, 341 is 1/3 *1023
	if dir == 1:
		f = pulse
		l = 0
		b = 0
		r = 0
	elif dir == 2
		f = 0
		l = pulse
		b = 0
		r = 0
	elif dir == 3:
		f = 0
		l = 0
		b = pulse
		r = 0
	elif dir == 4:
		f = 0
		l = 0
		b = 0
		r = pulse
	else
		f = 0
		l = 0
		b = 0
		r = 0

	Pf.duty(f)
	Pl.duty(l)
	Pb.duty(b)
	Pr.duty(r)

def connect_and_subscribe():
	global client_id, mqtt_server, topic_sub
	client = MQTTClient(client_id, mqtt_server)
	client.set_callback(sub_cb)
	client.connect()
	client.subscribe(topic_sub)
	print('connected to %s MQTT broker, subscribed to %s topic' %(mqtt_server, topic_sub))
	return client

def restart_and_reconnect():
	print('Failed to connect to MQTT broker. Reconnecting ...')
	timme.sleep(2)
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
