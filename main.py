from machine import I2C, Pin
import time
from time import ticks_add, ticks_diff
from random import randint
import flipper_scan

counter = 0
# Enable flame LED on SAO 1 GPIO 2
GPIOs[0][1].value(1)

clown_timeout = 2000 #ms
clown_deadline = ticks_add(time.ticks_ms(), clown_timeout)
# Enable clown nose on SAO2 GPIO 1
clown_pin = GPIOs[1][0]
clown_pin.value(True)
def tick_clown():
    global clown_deadline, clown_timeout
    if ticks_diff(time.ticks_ms(), clown_deadline) > 0:
        clown_pin.value(not clown_pin.value())
        clown_deadline = ticks_add(time.ticks_ms(), clown_timeout) #+randint(0,200))

#print(f'now:\t\t{time.ticks_ms()}')
#print(f'deadline:\t{deadline}')

def animate_spiral():
    ## do a quick spiral to test
    if petal_bus:
        for j in range(8):
            which_leds = (1 << (j+1)) - 1 
            for i in range(1,9):
                #print(which_leds)
                petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
                time.sleep_ms(30)
                petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
animate_spiral()
demo_timeout = 5000 #ms
demo_deadline = ticks_add(time.ticks_ms(), demo_timeout)
def reset_demo():
    global demo_deadline, demo_timeout
    demo_deadline = ticks_add(time.ticks_ms(), demo_timeout)
def run_demo():
    global demo_deadline, demo_timeout
    if ticks_diff(time.ticks_ms(), demo_deadline) > 0:
        animate_spiral()
        reset_demo()

def map_range(value, old_min=70, old_max=100, new_min=20, new_max=1000):
    # Ensure value is within the original range
    if value < old_min:
        value = old_min
    elif value > old_max:
        value = old_max
    
    # Perform the mapping
    new_value = new_min + ( (value - old_min) / (old_max - old_min) ) * (new_max - new_min)
    return new_value

# Set up flipper scanning
devices = flipper_scan.scan_ble_devices()
def get_flipper_strength():
    global devices
    # Purge old devices
    flipper_scan.purge_old_devices(devices)
    
    # Sort devices by RSSI in descending order
    sorted_devices = sorted(devices.values(), key=lambda d: d["rssi"], reverse=True)
    
    # Display sorted devices
    print("\nDevices sorted by strongest RSSI:")
    for i, device in enumerate(sorted_devices, 1):
        print(f"{i}: {device['name']} (RSSI: {device['rssi']}, Last Seen: {int(time.time() - device['last_seen'])} seconds ago)")
    try:
        number = 0-sorted_devices[0]['rssi']
        return int(map_range(number))
    except IndexError:
        return None

flipper_timeout = 5000 #ms
flipper_deadline = ticks_add(time.ticks_ms(), flipper_timeout)
while True:
    if ticks_diff(time.ticks_ms(), flipper_deadline) > 0:
        flipper_deadline = ticks_add(time.ticks_ms(), flipper_timeout)
        # Toggle the clown nose every 1s unless there's a flipper
        clown_timeout = get_flipper_strength()
        if not clown_timeout:
            clown_timeout = 2000
        else:
            clown_timeout = clown_timeout*2
        
    #print(ticks_diff(time.ticks_ms(), deadline))
    #run_demo()
        
    # Toggle clown nose if necessary
    tick_clown()

    ## display button status on RGB
    if petal_bus:
        if not buttonA.value():
            reset_demo()
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))

        if not buttonB.value():
            reset_demo()
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))

        if not buttonC.value():
            reset_demo()
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x00]))

    ## see what's going on with the touch wheel
    if touchwheel_bus:
        tw = touchwheel_read(touchwheel_bus)

    ## display touchwheel on petal
    if petal_bus and touchwheel_bus:
        if tw > 0:
            reset_demo()
            tw = (128 - tw) % 256 
            petal = int(tw/32) + 1
        else: 
            petal = 999
        for i in range(1,9):
            if i == petal:
                petal_bus.writeto_mem(0, i, bytes([0x7F]))
            else:
                petal_bus.writeto_mem(0, i, bytes([0x00]))
    
    time.sleep_ms(20)
    bootLED.off()






