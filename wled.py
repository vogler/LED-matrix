# based on https://github.com/scottlawsonbc/audio-reactive-led-strip/blob/master/python/led.py
# via https://kno.wled.ge/interfaces/udp-realtime/#setup-with-arls

# inlined from config.py
UDP_IP = 'wled-matrix'
UDP_PORT = 21324
N_PIXELS = 256

import numpy as np
import socket
_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

pixels = np.tile(1, (3, N_PIXELS))
_prev_pixels = np.tile(253, (3, N_PIXELS))

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
    pixels = np.clip(pixels, 0, 255).astype(int) # truncate values and cast to integer
    idx = range(pixels.shape[1]) # pixel indices
    idx = [i for i in idx if not np.array_equal(pixels[:, i], _prev_pixels[:, i])] # indices where value changed
    MAX_PIXELS_PER_PACKET = 126
    n_packets = len(idx) // MAX_PIXELS_PER_PACKET + 1
    idx = np.array_split(idx, n_packets)
    for packet_indices in idx:
        m = []
        # packet header: https://kno.wled.ge/interfaces/udp-realtime/#udp-realtime
        m.append(1) # protocol: WARLS (WLED Audio-Reactive-Led-Strip)
        m.append(2) # wait 2s after the last received packet before returning to normal mode
        for i in packet_indices:
            m.append(i)  # Index of pixel to change
            m.append(pixels[0][i])  # Pixel red value
            m.append(pixels[1][i])  # Pixel green value
            m.append(pixels[2][i])  # Pixel blue value
        _sock.sendto(bytes(m), (UDP_IP, UDP_PORT))
    _prev_pixels = np.copy(pixels)

# Execute this file to run a LED strand test.
# You should see a red, green, and blue pixel scroll across the LED strip continuously.
if __name__ == '__main__':
    import time
    # Turn all pixels off
    pixels *= 0
    pixels[0, 0] = 255  # Set 1st pixel red
    pixels[1, 1] = 255  # Set 2nd pixel green
    pixels[2, 2] = 255  # Set 3rd pixel blue
    print('Starting LED strand test')
    while True:
        pixels = np.roll(pixels, 1, axis=1)
        update()
        time.sleep(.05)
