from machine import UART, Pin
import time

led = Pin("LED", Pin.OUT)
uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))


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


print("Begin reading distance:")

while True:
    led.on()
    print(f"{us100_read_distance(uart1)} cm\t{us100_read_temperature(uart1)}°C")
    led.off()
    time.sleep(0.5)
