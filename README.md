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
$ mpremote connect port:/dev/tty.usbmodem14101 mip install github:robert-hh/BME280/bme280_float.py
```

### Setup Homebridge

Add accessory to `config.json` of homebridge:

```json
{
    "bridge": {...},
    "accessories": [
        ...,
        {
            "type": "leakSensor",
            "name": "Water Level Sensor 01",
            "url": "broker.emqx.io",
            "logMqtt": true,
            "codec": "waterlevel.js",
            "topics": {
                "getOnline": "moritzmhmk/sensor_01",
                "getBatteryLevel": "moritzmhmk/sensor_01",
                "getLeakDetected": "moritzmhmk/sensor_01",
                "getWaterLevel": "moritzmhmk/sensor_01",
            },
            "accessory": "mqttthing"
        }
    ],
    "platforms": [...]
}
```

Create "codec" file `waterlevel.js` in the same path as the config.json.
