import board
import neopixel
import i2ctarget

I2C_ADDR = 0x33
WIDTH = 32
HEIGHT = 4
PIXELS = WIDTH * HEIGHT
MAGIC = 0xA5

pixels = neopixel.NeoPixel(board.GP0, PIXELS, brightness=0.08, auto_write=False)
rx = bytearray(6)

anim_phase = 0
mode = 1
status = 0
accent = 0
level = 24


def wheel(pos, phase):
    wave = (pos * 5 + phase) & 0xFF
    if wave < 85:
        return (wave * 2, 90 - wave, 12)
    if wave < 170:
        wave -= 85
        return (170 - wave, 12, wave * 2)
    wave -= 170
    return (12, wave * 2, 170 - wave)


def draw_status_bar(bits):
    colors = (
        (0, 48, 16), # macropad connected (green)
        (48, 30, 0), # sliderpad connected (orange)
        (36, 0, 40), # matrix connected (purple)
        (0, 0, 40),  # spare status (blue)
    )
    for i in range(4):
        if bits & (1 << i):
            pixels[i] = colors[i]
        else:
            pixels[i] = (0, 0, 0)


def draw_base_wave(phase):
    for i in range(4, PIXELS):
        pixels[i] = wheel(i, phase)


def draw_fn_wave(phase):
    for i in range(4, PIXELS):
        x = i % WIDTH
        pixels[i] = (8, (x * 5 + phase) & 0x3F, 36)


def apply_frame():
    draw_status_bar(status)
    if mode == 2:
        draw_fn_wave(anim_phase)
    else:
        draw_base_wave(anim_phase)
    pixels.show()


with i2ctarget.I2CTarget(board.GP9, board.GP8, (I2C_ADDR,)) as device:
    while True:
        r = device.request()
        if r:
            with r:
                if not r.is_read:
                    data = r.read(6)
                    if data and len(data) == 6 and data[0] == MAGIC:
                        mode = data[1]
                        anim_phase = data[2]
                        status = data[3]
                        accent = data[4]
                        level = data[5]
        
        apply_frame()
