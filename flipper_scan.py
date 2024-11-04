import time
import bluetooth

_IRQ_SCAN_RESULT = 5
PURGE_TIMEOUT = 20  # Time in seconds to keep devices if not heard again

def decode_name(adv_data):
    """Extract the name from advertisement data if available."""
    adv_data = bytes(adv_data)
    i = 0
    while i < len(adv_data):
        length = adv_data[i]
        if length == 0:
            break
        type = adv_data[i + 1]
        # Type 0x09 is the Complete Local Name AD type
        if type == 0x09:
            return adv_data[i + 2:i + 2 + length - 1].decode('utf-8')
        i += 1 + length
    return None

def scan_ble_devices():
    # Initialize the Bluetooth adapter in scan mode
    ble = bluetooth.BLE()
    ble.active(True)

    # Store discovered devices with names containing "flipper"
    devices = {}

    def bt_irq(event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            device_name = decode_name(adv_data)
            
            if device_name and "flipper" in device_name.lower():
                # Use address as unique identifier to avoid duplicates
                addr_str = ':'.join('{:02X}'.format(b) for b in addr)
                current_time = time.time()
                
                # Update or add the device with RSSI and last seen timestamp
                devices[addr_str] = {
                    "name": device_name,
                    "rssi": rssi,
                    "last_seen": current_time
                }
                print("name: ", device_name, "rssi: ", rssi)

    # Set up the Bluetooth IRQ handler
    ble.irq(bt_irq)

    # Start scanning (continuous mode)
    print("Scanning for BLE devices...")
    ble.gap_scan(0, 30000, 30000, True)  # 0 duration means continuous scanning

    return devices

def purge_old_devices(devices):
    """Remove devices not seen for longer than PURGE_TIMEOUT seconds."""
    current_time = time.time()
    to_remove = [addr for addr, info in devices.items() if current_time - info["last_seen"] > PURGE_TIMEOUT]
    for addr in to_remove:
        print(f"Purging device {devices[addr]['name']} (Address: {addr}) - last seen {int(current_time - devices[addr]['last_seen'])} seconds ago")
        del devices[addr]

# Run the scan function
if __name__ == "__main__":
    devices = scan_ble_devices()
    while True:
        # Purge old devices
        purge_old_devices(devices)
        
        # Sort devices by RSSI in descending order
        sorted_devices = sorted(devices.values(), key=lambda d: d["rssi"], reverse=True)
        
        # Display sorted devices
        print("\nDevices sorted by strongest RSSI:")
        for i, device in enumerate(sorted_devices, 1):
            print(f"{i}: {device['name']} (RSSI: {device['rssi']}, Last Seen: {int(time.time() - device['last_seen'])} seconds ago)")
        
        try:
            print("hottest: ", 0-sorted_devices[0]['rssi'])
        except IndexError:
            pass
        time.sleep(5)
