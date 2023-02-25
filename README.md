# rpi-pico-waterlevel-sensor
 
## Setup Development Environment 

Create venv:
```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Install stubs:
```bash
$ pip install micropython-rp2-stubs
```

## Install dependencies on device

Install mpremote
```bash
$ pip install mpremote
```

```bash
$ mpremote connect port:/dev/tty.usbmodem14101 mip install umqtt.simple
```
