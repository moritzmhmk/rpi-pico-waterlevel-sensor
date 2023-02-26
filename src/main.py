from machine import UART, I2C, Pin, RTC
import time
import struct
import network
import socket
import json

from umqtt.simple import MQTTClient
import bme280_float as bme280

import env


def connect_to_network(nic: network.WLAN, ssid: str, password: str):
    print(f"Connecting to network \"{ssid}\"...", end="")
    nic.active(True)
    nic.connect(ssid, password)
    for _ in range(10):
        s = nic.status()
        if s == 3:
            print(" done.")
            break
        if s >= 0:
            time.sleep(1)
            print(".", end="")
            continue
        if s == -1:
            print(" failed!")
        if s == -2:
            print(" no network!")
        if s == -3:
            print(" bad authentication!")

        raise RuntimeError('Network connection failed.')


def set_time_from_ntp(host: str = "pool.ntp.org"):
    NTP_DELTA = 2208988800
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    t = val - NTP_DELTA
    tm = time.gmtime(t)
    RTC().datetime(
        (tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))


def time_to_iso(t: time.struct_time):
    Y, m, d, H, M, S, *_ = t
    return f"{Y}-{m:02}-{d:02}T{H:02}:{M:02}:{S:02}Z"


def us100_read_distance(uart: UART) -> float | None:
    for _ in range(2):
        uart.write(b"\x55")
        time.sleep(0.1)
        data = uart.read(2)
        if data and len(data) == 2:
            return (data[1] + (data[0] << 8)) / 10
        time.sleep(0.1)
    return None


def us100_read_temperature(uart: UART) -> int | None:
    for _ in range(2):
        uart.write(b"\x50")
        time.sleep(0.1)
        data = uart.read(1)
        if data and len(data) == 1:
            return data[0] - 45
        time.sleep(0.1)
    return None


if __name__ == "__main__":
    led_pin = Pin("LED", mode=Pin.OUT, value=1)
    done_pin = Pin(15, mode=Pin.OUT, value=0)
    try:
        uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
        i2c = I2C(1, sda=Pin(6), scl=Pin(7))
        bme = bme280.BME280(i2c=i2c)

        temperature, pressure, humidity = bme.read_compensated_data()

        us100_read_distance(uart1)  # discard first measurement
        distance = us100_read_distance(uart1)

        wlan = network.WLAN(network.STA_IF)
        connect_to_network(wlan, env.WLAN_SSID, env.WLAN_PASSWORD)

        set_time_from_ntp()
        timestamp = time_to_iso(time.gmtime())

        # MQTT
        client = MQTTClient(env.MQTT_CLIENT_ID,
                            env.MQTT_SERVER, keepalive=3600)
        client.connect()
        print(
            f"Connected to mqtt on \"{env.MQTT_SERVER}\" as \"{env.MQTT_CLIENT_ID}\"."
        )
        payload = {
            'distance': distance,
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
            'timestamp': timestamp
        }
        topic = f"{env.MQTT_BASE_TOPIC}/sensor_01"
        client.publish(topic, json.dumps(payload), retain=True)
        print(f"Published payload \"{payload}\" in topic \"{topic}\".")
        client.disconnect()
        print("Disconnected from mqtt server.")
    except Exception as e:
        print(f"Esception {e} occured.")
        print(e)
    finally:
        # Blink LED
        for _ in range(5*2):
            led_pin.toggle()
            time.sleep(0.1)

        # Signal TPL5110 to shutdown power
        while True:
            led_pin.toggle()
            done_pin.toggle()
            time.sleep(0.5)
