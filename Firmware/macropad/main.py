import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_displayio_ssd1306 import SSD1306
from digitalio import DigitalInOut, Direction, Pull
import i2ctarget
from common import make_packet

ROWS = (board.GP0, board.GP1, board.GP2, board.GP3)
COLS = (board.GP4, board.GP5, board.GP6, board.GP7)
OLED_SDA = board.GP8
OLED_SCL = board.GP9
packet = make_packet(1)

displayio.release_displays()
i2c = busio.I2C(scl=OLED_SCL, sda=OLED_SDA, frequency=400000)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = SSD1306(display_bus, width=128, height=64)
root = displayio.Group()
root.append(label.Label(terminalio.FONT, text='lattice macropad', x=0, y=8))
count_label = label.Label(terminalio.FONT, text='keys: 0', x=0, y=20)
root.append(count_label)
cell_tiles = []
for idx in range(16):
    x = (idx % 4) * 30
    y = 28 + (idx // 4) * 9
    bmp = displayio.Bitmap(24, 7, 2)
    pal = displayio.Palette(2)
    pal[0] = 0x000000
    pal[1] = 0xFFFFFF
    tile = displayio.TileGrid(bmp, pixel_shader=pal, x=x, y=y)
    root.append(tile)
    cell_tiles.append(bmp)
display.root_group = root

rows = []
cols = []
for pin in ROWS:
    io = DigitalInOut(pin)
    io.direction = Direction.OUTPUT
    io.value = True
    rows.append(io)
for pin in COLS:
    io = DigitalInOut(pin)
    io.direction = Direction.INPUT
    io.pull = Pull.UP
    cols.append(io)


def popcount(value):
    count = 0
    while value:
        count += value & 1
        value >>= 1
    return count


def scan_keys():
    mask = 0
    for r, row in enumerate(rows):
        row.value = False
        for c, col in enumerate(cols):
            if not col.value:
                mask |= 1 << (r * 4 + c)
        row.value = True
    return mask


def draw_cells(mask):
    count_label.text = 'keys: {}'.format(popcount(mask))
    for idx, bmp in enumerate(cell_tiles):
        pressed = bool(mask & (1 << idx))
        for x in range(24):
            for y in range(7):
                edge = x == 0 or x == 23 or y == 0 or y == 6
                fill = pressed and 1 < x < 22 and 1 < y < 5
                bmp[x, y] = 1 if edge or fill else 0


def refresh_packet(mask):
    packet[7] = mask & 0xFF


def module_packet():
    return packet


last_mask = -1

with i2ctarget.I2CTarget(board.GP27, board.GP26, (0x31,)) as device:
    while True:
        mask = scan_keys()
        if mask != last_mask:
            refresh_packet(mask)
            draw_cells(mask)
            last_mask = mask

        r = device.request()
        if r:
            with r:
                if r.is_read:
                    r.write(packet)