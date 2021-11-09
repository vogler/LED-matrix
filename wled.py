# based on https://github.com/scottlawsonbc/audio-reactive-led-strip/blob/master/python/led.py
# via https://kno.wled.ge/interfaces/udp-realtime/#setup-with-arls

# inlined from config.py
UDP_IP = 'wled-matrix'
UDP_PORT = 21324
w = 16
h = 16
n = w*h

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

# Execute this file to run a LED strand test.
# You should see a red, green, and blue pixel scroll across the LED strip continuously.
if __name__ == '__main__':
    import time
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
