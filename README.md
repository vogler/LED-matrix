# LED-matrix
16x16 pixel RGB LED matrix with support for [WLED](https://github.com/Aircoookie/WLED) and text (digits only for now).

Use WLED and its interfaces for controlling the light and showing effects.
To show digits (which WLED can't), see `wled.py` which sends pixel information to WLED via UDP.

Run a server taking commands via MQTT on `lights/wled-matrix` with `python3 wled.py mqtt`.
Commands are `on, off, num 123, co2`.

Grid and case were designed in Fusion 360: https://a360.co/36UBWL9

You can 3D print the `.stl` files in `models`.
Beware of warping (visible in top right corner below).

![image](https://user-images.githubusercontent.com/493741/156219889-854490f8-e715-45d4-9400-5dd8a94ac959.png)
![image](https://user-images.githubusercontent.com/493741/156219938-665f8553-356a-4c82-9fce-6b1e8f622a15.png)


### Log
<details>
  <summary>Click to expand</summary>

01.03.22 Created this repo and [extracted commits](https://www.pixelite.co.nz/article/extracting-file-folder-from-git-repository-with-full-git-history/) from [smart-home](https://github.com/vogler/smart-home/search?q=wled&type=commits):
```console
$ cd smart-home
$ git log --pretty=email --patch-with-stat --reverse --full-index --binary -- audio-reactive-led-strip wled.py > ../patch
$ cd ../LED-matrix
$ git am < ../patch
```
</details>
