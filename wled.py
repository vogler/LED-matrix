# based on https://github.com/scottlawsonbc/audio-reactive-led-strip/blob/master/python/led.py
# via https://kno.wled.ge/interfaces/udp-realtime/#setup-with-arls

# inlined from config.py
HOST = 'wled-matrix'
UDP_PORT = 21324
W = 16 # width pixels
H = 16 # height pixels
MQTT_BROKER = 'localhost'
MQTT_TOPIC = 'lights/wled-matrix'
MQTT_CO2_TOPIC = 'sensors/mh-z19b'
MQTT_TH_TOPIC = 'sensors/bme280'

import time
import numpy as np
import socket
_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

pixels = np.full((H,W,3), 0, np.uint8)
prev_pixels = np.copy(pixels)

def update():
    """Sends UDP packets to ESP8266 to update LED strip values

    The packet encoding scheme is:
        |i|r|g|b|
    where
        i (0 to 255): Index of LED to change (zero-based)
        r (0 to 255): Red value of LED
        g (0 to 255): Green value of LED
        b (0 to 255): Blue value of LED
    """
    global pixels, prev_pixels
    idx = [(y,x) for y in range(H) for x in range(W) if (pixels[y,x] != prev_pixels[y,x]).any()] # indices where value changed
    MAX_PIXELS_PER_PACKET = 126
    n_packets = len(idx) // MAX_PIXELS_PER_PACKET + 1
    packets = np.array_split(idx, n_packets)
    try:
        for idx in packets:
            m = []
            # packet header: https://kno.wled.ge/interfaces/udp-realtime/#udp-realtime
            m.append(1) # protocol: WARLS (WLED Audio-Reactive-Led-Strip)
            m.append(2) # wait 2s after the last received packet before returning to normal mode
            for (y,x) in idx:
                # zig-zag layout: 0 starts top left going down but then second column goes up
                index = x*H + (H-1-y if x%2 else y)
                m.append(index)
                m.extend(pixels[y,x]) # RGB values
            _sock.sendto(bytes(m), (HOST, UDP_PORT))
    except Exception as e:
        print('update failed:', e)
    prev_pixels = np.copy(pixels)

def clear():
    global pixels
    pixels *= 0 # Turn all pixels off

# Scrolls a red, green, and blue pixel across the LED matrix continuously
def strand():
    global pixels
    clear()
    pixels[0, 0] = [255, 0, 0] # red
    pixels[1, 0] = [0, 255, 0] # green
    pixels[2, 0] = [0, 0, 255] # blue
    print('Starting LED strand test')
    i = 0
    while True:
        pixels = np.roll(pixels, 1, 0 if i%17 else 1)
        i = (i+1) % 256
        update()
        time.sleep(.05)


digits = {}
digits[0] = [[1,1,1],
             [1,0,1],
             [1,0,1],
             [1,0,1],
             [1,1,1]]
digits[1] = [[0,0,1],
             [0,1,1],
             [0,0,1],
             [0,0,1],
             [0,0,1]]
digits[1] = [[0,1,0],
             [1,1,0],
             [0,1,0],
             [0,1,0],
             [1,1,1]]
digits[2] = [[1,1,1],
             [0,0,1],
             [1,1,1],
             [1,0,0],
             [1,1,1]]
digits[3] = [[1,1,1],
             [0,0,1],
             [1,1,1],
             [0,0,1],
             [1,1,1]]
digits[4] = [[1,0,1],
             [1,0,1],
             [1,1,1],
             [0,0,1],
             [0,0,1]]
digits[5] = [[1,1,1],
             [1,0,0],
             [1,1,1],
             [0,0,1],
             [1,1,1]]
digits[6] = [[1,1,1],
             [1,0,0],
             [1,1,1],
             [1,0,1],
             [1,1,1]]
digits[7] = [[1,1,1],
             [0,0,1],
             [0,1,0],
             [0,1,0],
             [0,1,0]]
digits[8] = [[1,1,1],
             [1,0,1],
             [1,1,1],
             [1,0,1],
             [1,1,1]]
digits[9] = [[1,1,1],
             [1,0,1],
             [1,1,1],
             [0,0,1],
             [1,1,1]]

colors = {
    "black":   [0, 0, 0],
    "red":     [255, 0, 0],
    "yellow":  [255, 255, 0],
    "lime":    [0, 255, 0],
    "blue":    [0, 0, 255],
    "cyan":    [0, 255, 255],
    "magenta": [255, 0, 255],
    "white":   [255, 255, 255],
    # all the 128 variations are the same as above, just a little bit less bright
    "gray":    [128, 128, 128],
    "maroon":  [128, 0, 0],
    "green":   [0, 128, 0],
    "navy":    [0, 0, 128],
    "olive":   [128, 128, 0],
    "teal":    [0, 128, 128],
    "purple":  [128, 0, 128],
    # some inbetween colors
    "orange":  [255, 165, 0],
    "coral":   [255, 127, 80], # same as orange
    "forest":  [34, 139, 34],
    "cadet":   [95, 158, 160],
    "steel":   [70, 130, 180],
    "cornflower": [100, 149, 237],
    "plum":    [221, 160, 221],
}

# place RGB pixels p at position x, y
def place(p, x, y):
    global pixels
    for py in range(len(p)):
        for px in range(len(p[0])):
            if p[py][px]:
                pixels[y+py, x+px] = p[py][px]

# color a mask m (entries 0 or 1), bg is optional background fill color
def color_mask(color, m, bg=None):
    o = {}
    for y in range(len(m)):
        o[y] = {}
        for x in range(len(m[0])):
            o[y][x] = color if m[y][x] == 1 else bg
    return o

# example: place(color_mask(colors["red"], digits[4]), 1, 1)

# show a number n at position x, y with spacing between digits and rotating colors
# x=0 is ltr, x=-1 is rtl starting at x=15; default colors without the first (black)
def show_number(n, x=-2, y=5, spacing=1, colors=list(colors.values())[1:], bg=colors['black']):
    ds = [int(c) for c in str(n)]
    dl = len(digits[0][0])
    dw = dl + spacing
    if x < 0:
        x += W - dl+1
        dw *= -1
        ds.reverse()
    for i in range(len(ds)):
        color = colors[(len(ds)-1-i)%len(colors)]
        p = color_mask(color, digits[ds[i]], bg)
        place(p, x+i*dw, y)

# https://kno.wled.ge/interfaces/mqtt/ subscribe to brightness changes (>0 is on): mosquitto_sub -t wled/matrix/g
# https://kno.wled.ge/interfaces/json-api/
import requests
# https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request
from requests.adapters import HTTPAdapter, Retry
s = requests.Session()
retries = Retry(total=5, backoff_factor=0.2)
s.mount('http://', HTTPAdapter(max_retries=retries))

def is_on():
    try:
        return requests.get(f'http://{HOST}/json/state').json()['on']
    except Exception as e:
        print('is_on failed:', e)
        return False

def set_on(on): # doc says "t" should toggle, but does not work (also their curl example) -> only bool
    if type(on) is str: on = on == 'on' # on -> True | _ -> False
    try:
        requests.post(f'http://{HOST}/json/state', json = {'on': on})
    except Exception as e:
        print('set_on failed:', e)

def usage():
    print('usage: python3 %s [cmd]' % sys.argv[0])
    print('[cmd]:')
    print('\ton|off\tturn on/off')
    print('\tnum [n]\tshow number n in colors until killed')
    print('\tco2\tshow co2 level updated via MQTT in colors until killed')
    print('\tco2th\tshow co2 level + temperature + humidity - updated via MQTT in colors until killed')
    print('\tmqtt\tsubscribe to %s for the above commands (numeric payload for num)' % MQTT_TOPIC)
    quit(1)

import paho.mqtt.client as mqtt
import json
from threading import Lock
mutex = Lock() # protect pixels, otherwise we get races updating them
is_showing = False
data = dict()

def show_co2x():
    global data
    clear() # TODO only needed if the number of digits changes...
    if data['cmd'] == 'co2':
        show_number(data['co2'])
    if data['cmd'] == 'co2th':
        if 'co2' in data: show_number(data['co2'], y=2)
        if 'temp' in data: show_number(round(data['temp']), y=9, x=0, colors=[colors['purple']])
        if 'humi' in data: show_number(round(data['humi']), y=9, x=8, colors=[colors['teal']])

def on_message(client, userdata, msg):
    global data
    # print(msg.topic, str(msg.payload))
    mutex.acquire()
    if msg.topic == MQTT_CO2_TOPIC:
        co2 = data['co2'] = json.loads(msg.payload)['co2']
        print('co2:', co2)
        show_co2x()
    elif msg.topic == MQTT_TH_TOPIC:
        j = json.loads(msg.payload)
        t = data['temp'] = j['temperature']
        h = data['humi'] = j['humidity']
        print('temp:', t, 'humi:', round(h, 2))
        show_co2x()
    elif msg.topic == MQTT_TOPIC:
        m = msg.payload.decode('utf-8')
        client.unsubscribe(MQTT_CO2_TOPIC)
        client.unsubscribe(MQTT_TH_TOPIC)
        print('MQTT cmd:', m)
        time.sleep(1) # TODO better solution
        clear()
        if m == '0': m = 'off'
        data['cmd'] = m
        if m in ['on', 'off']:
            set_on(m)
        elif m.isnumeric():
            set_on(True)
            show_number(int(m))
        elif m == 'co2':
            set_on(True)
            client.subscribe(MQTT_CO2_TOPIC)
        elif m == 'co2th':
            set_on(True)
            client.subscribe(MQTT_CO2_TOPIC)
            client.subscribe(MQTT_TH_TOPIC)
        else:
            print('MQTT: unhandled payload', m)
    mutex.release()

client = mqtt.Client()
client.on_connect = lambda client, userdata, flags, rc: print("Connected to MQTT (code %d) " % rc)
client.on_message = on_message

if __name__ == '__main__':
    import sys
    argc = len(sys.argv)
    if argc < 2: usage()
    cmd = data['cmd'] = sys.argv[1].lower()
    was_on = is_on()
    print('was_on', was_on)
    should_be_on = cmd != 'off' and cmd != 'mqtt'
    if was_on != should_be_on: set_on(should_be_on)
    try:
        if cmd in ['on', 'off']:
            pass
        elif cmd == 'num':
            if argc != 3: usage()
            num = int(sys.argv[2])
            show_number(num)
            while True:
                update()
        elif cmd in ['co2', 'co2th', 'mqtt']:
            client.connect(MQTT_BROKER)
            if cmd == 'mqtt':
                client.subscribe(MQTT_TOPIC)
            elif cmd == 'co2':
                client.subscribe(MQTT_CO2_TOPIC)
            elif cmd == 'co2th':
                client.subscribe(MQTT_CO2_TOPIC)
                client.subscribe(MQTT_TH_TOPIC)
            # client.loop_forever() # blocks, but co2 comes only every 10s, w/o update() WLED goes back to normal mode
            client.loop_start() # starts a thread; could also use client.loop() below, but not as responsive.
            while True:
                mutex.acquire()
                update()
                mutex.release()
                time.sleep(1)
        else:
            usage()
    except KeyboardInterrupt:
        print('exit')
    finally:
        if not was_on and cmd != 'on' and cmd != 'off':
            clear()
            update()
            time.sleep(1) # give time to process last UDP packets, otherwise it does not turn off
            set_on(False)
            print('turned off again')
