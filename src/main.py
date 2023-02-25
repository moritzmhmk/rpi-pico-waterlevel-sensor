from machine import UART, Pin
import time
import network
from umqtt.simple import MQTTClient

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


def toggle(pin: Pin, times: int, delay: float):
    for _ in range(times):
        pin.off()
        time.sleep(delay)
        pin.on()
        time.sleep(delay)


if __name__ == "__main__":
    led_pin = Pin("LED", mode=Pin.OUT, value=1)
    done_pin = Pin(15, mode=Pin.OUT, value=0)
    uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))

    us100_read_distance(uart1)  # discard first measurement
    distance = us100_read_distance(uart1)

    wlan = network.WLAN(network.STA_IF)
    connect_to_network(wlan, env.WLAN_SSID, env.WLAN_PASSWORD)
    client = MQTTClient(env.MQTT_CLIENT_ID, env.MQTT_SERVER, keepalive=3600)
    client.connect()
    print(
        f"Connected to mqtt on \"{env.MQTT_SERVER}\" as \"{env.MQTT_CLIENT_ID}\"."
    )
    client.publish(f"{env.MQTT_BASE_TOPIC}/distance", f"{distance}")
    client.disconnect()
    print("Disconnected from mqtt server.")

    # Blink LED
    toggle(led_pin, 5, 0.1)
    # Signal TPL5110 to shutdown power
    toggle(done_pin, 5, 0.5)

    # Everything below this line will only execute when TPL5110 is not in use - e.g. while debugging
    print("Starting debug loop.")
    while True:
        toggle(led_pin, 3, 0.05)
        print(f"{us100_read_distance(uart1)} cm\t{us100_read_temperature(uart1)}°C")
        time.sleep(0.5)
