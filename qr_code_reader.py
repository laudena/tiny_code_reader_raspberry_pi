import smbus2
import struct
import time

from smbus2 import SMBus, i2c_msg

I2C_BUS = 1      # I2C bus (usually 1 on Raspberry Pi)
I2C_ADDR = 0x0C  # Change this if your device has a different address. execute this command to find that address: i2cdetect -y 1
MAX_LENGTH = 254
I2C_READ_CHUNK_SIZE = 32  # Maximum bytes per I2C transaction

bus = SMBus(I2C_BUS)

def read_tiny_code_reader():
    try:
        # Step 1: Read first 2 bytes for content length
        write = i2c_msg.write(I2C_ADDR, [0x00])  # Set pointer to 0
        read = i2c_msg.read(I2C_ADDR, 2)  # Read 2 bytes
        bus.i2c_rdwr(write, read)
        raw_length = list(read)

        if len(raw_length) < 2:
            print("x", end="", flush=True)
            return None

        content_length = struct.unpack("<H", bytes(raw_length))[0]

        # Validate length
        if content_length == 0 or content_length > MAX_LENGTH:
            print(".", end="", flush=True)
            return None

        # Step 2: Read the full content in one transaction
        read = i2c_msg.read(I2C_ADDR, content_length + 2)
        bus.i2c_rdwr(read)
        content_bytes = list(read)[2:]

        return {
            "content_length": content_length,
            "content_bytes": bytes(content_bytes)
        }

    except Exception as e:
        print(f"\nError reading from I2C: {e}", end="", flush=True)
        return None

# Main loop to read the qr-code periodically
while True:
    message = read_tiny_code_reader()
    if message:
        print(f"Length: {message['content_length']}, Content: {message['content_bytes'].decode('utf-8', errors='ignore')}")
    time.sleep(0.25) # Adjust delay as needed
