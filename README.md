# LED-matrix
16x16 pixel RGB LED matrix with support for [WLED](https://github.com/Aircoookie/WLED) and text (digits only for now).


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
