# based on https://github.com/scottlawsonbc/audio-reactive-led-strip/blob/master/python/led.py
# via https://kno.wled.ge/interfaces/udp-realtime/#setup-with-arls

# inlined from config.py
UDP_IP = 'wled-matrix'
UDP_PORT = 21324
w = 16
h = 16
n = w*h

import time
import numpy as np
import socket
_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

pixels = np.full((h,w,3), 0, np.uint8)
_prev_pixels = np.copy(pixels)

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
    global pixels, _prev_pixels
    idx = [(y,x) for y in range(h) for x in range(w) if (pixels[y,x] != _prev_pixels[y,x]).any()] # indices where value changed
    MAX_PIXELS_PER_PACKET = 126
    n_packets = len(idx) // MAX_PIXELS_PER_PACKET + 1
    packets = np.array_split(idx, n_packets)
    for idx in packets:
        m = []
        # packet header: https://kno.wled.ge/interfaces/udp-realtime/#udp-realtime
        m.append(1) # protocol: WARLS (WLED Audio-Reactive-Led-Strip)
        m.append(2) # wait 2s after the last received packet before returning to normal mode
        for (y,x) in idx:
            # zig-zag layout: 0 starts top left going down but then second column goes up
            index = x*h + (h-1-y if x%2 else y)
            m.append(index)
            m.extend(pixels[y,x]) # RGB values
        _sock.sendto(bytes(m), (UDP_IP, UDP_PORT))
    _prev_pixels = np.copy(pixels)

# Scrolls a red, green, and blue pixel across the LED matrix continuously
def strand():
    global pixels
    pixels *= 0 # Turn all pixels off
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
             [1,0,0]]
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
    "black":  [0, 0, 0],
    "red":    [255, 0, 0],
    "green":  [0, 255, 0],
    "blue":   [0, 0, 255],
    "yellow": [255, 255, 0],
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
def show_number(n, x=-2, y=1, spacing=1, colors=list(colors.values())[1:]):
    ds = [int(c) for c in str(n)]
    dl = len(digits[0][0])
    dw = dl + spacing
    if x < 0:
        x += w - dl+1
        dw *= -1
        ds.reverse()
        colors.reverse()
    for i in range(len(ds)):
        p = color_mask(colors[i%len(colors)], digits[ds[i]])
        place(p, x+i*dw, y)

# https://kno.wled.ge/interfaces/mqtt/ subscribe to brightness changes (>0 is on): mosquitto_sub -t wled/matrix/g
# https://kno.wled.ge/interfaces/json-api/
import requests
def is_on():
    return requests.get('http://wled-matrix/json/state').json()['on']

def set_on(on): # doc says "t" should toggle, but does not work (also their curl example) -> only bool
    requests.post('http://wled-matrix/json/state', json = {'on': on})

def usage():
    print('usage: python3 %s [cmd]' % sys.argv[0])
    print('[cmd]:')
    print('\ton|off\tturn on/off')
    print('\tnum [n]\tshow number n in colors until killed')
    quit(1)

if __name__ == '__main__':
    import sys
    argc = len(sys.argv)
    if argc < 2: usage()
    cmd = sys.argv[1].lower()
    if cmd in ['on', 'off']:
        set_on(cmd == 'on')
    elif cmd == 'num':
        if argc != 3: usage()
        num = int(sys.argv[2])
        was_on = is_on()
        print('was_on', was_on)
        try:
            if not was_on: set_on(True)
            show_number(num)
            while True:
                update()
        except KeyboardInterrupt:
            print('exit')
        finally:
            if not was_on:
                time.sleep(1) # give time to process last UDP packets, otherwise it does not turn off
                set_on(False)
                print('turned off again')
    else:
        usage()
