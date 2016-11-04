# IPTV playlist checker
Unfortunately, it supports only unet.by for now.

## Requirements
### System packages
* python 3.5
* ffprobe (part of ffmpeg)

### Python modules
* ffmpy
* m3u8
* termcolor

## Usage
```
./iptv-checker.py [-h] [-s] [-v] playlist_uri

positional arguments:
  playlist_uri        playlist for check

optional arguments:
  -h, --help          show this help message and exit
  -s, --stop-on-fail  stop on first fail
  -v, --verbose       print additional info on fail
```
