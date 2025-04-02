import time
import busio
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# Initialize the onboard LED
led = digitalio.DigitalInOut(board.GP28)
led.direction = digitalio.Direction.OUTPUT
led.value = True

# Define rows and columns GPIOs
row_pins = [board.GP2, board.GP3, board.GP4, board.GP5, board.GP10]
col_pins = [board.GP6, board.GP7, board.GP8, board.GP9]

rows = [digitalio.DigitalInOut(pin) for pin in row_pins]
cols = [digitalio.DigitalInOut(pin) for pin in col_pins]

for row in rows:
    row.direction = digitalio.Direction.OUTPUT

for col in cols:
    col.direction = digitalio.Direction.INPUT
    col.pull = digitalio.Pull.DOWN

# Keypad layout
keys = [
    ['NumLock', 'Divide', 'Multiply', 'Subtract'],
    ['7', '8', '9', 'Subtract'],
    ['4', '5', '6', 'Add'],
    ['1', '2', '3', None],
    ['0', 'Period', 'Enter', None]
]

key_mapping = {
    "1": Keycode.ONE,
    "2": Keycode.TWO,
    "3": Keycode.THREE,
    "4": Keycode.FOUR,
    "5": Keycode.FIVE,
    "6": Keycode.SIX,
    "7": Keycode.SEVEN,
    "8": Keycode.EIGHT,
    "9": Keycode.NINE,
    "0": Keycode.ZERO,
    "Add": Keycode.KEYPAD_PLUS,
    "Subtract": Keycode.KEYPAD_MINUS,
    "Multiply": Keycode.KEYPAD_ASTERISK,
    "Divide": (Keycode.FORWARD_SLASH, Keycode.BACKSLASH),
    "Enter": Keycode.ENTER,
    "NumLock": Keycode.KEYPAD_NUMLOCK,
    "Period": Keycode.KEYPAD_PERIOD,
}

# Initialize HID Keyboard
kbd = Keyboard(usb_hid.devices)

# Initialize UART for serial communication
uart = busio.UART(board.GP0, board.GP1, baudrate=115200)

# Track previous button states
previous_states = [[False] * len(col_pins) for _ in range(len(row_pins))]

def send_key_to_serial(key_name):
    """Send key press to serial in a format C# can parse"""
    uart.write(f"KEYPRESS:{key_name}\n".encode())
    print(f"Sent: KEYPRESS:{key_name}")

while True:
    for row_idx, row in enumerate(rows):
        row.value = True
        for col_idx, col in enumerate(cols):
            current_state = col.value
            key_name = keys[row_idx][col_idx]
            
            if current_state and not previous_states[row_idx][col_idx] and key_name:
                # Send HID key press
                if key_name in key_mapping:
                    if isinstance(key_mapping[key_name], tuple):
                        # Handle keys with multiple options (like Divide)
                        kbd.press(key_mapping[key_name][0])
                    else:
                        kbd.press(key_mapping[key_name])
                    time.sleep(0.1)
                    kbd.release_all()
                
                # Send to serial for C# application
                send_key_to_serial(key_name)
                
            previous_states[row_idx][col_idx] = current_state
        row.value = False
    
    time.sleep(0.01)