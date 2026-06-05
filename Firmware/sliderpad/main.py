import analogio
import board
import rotaryio
import i2ctarget
from digitalio import DigitalInOut, Direction, Pull
from common import make_packet, write_i16

packet = make_packet(2)
slider_pins = (board.GP0, board.GP1, board.GP2)
enc_pins = ((board.GP3, board.GP4), (board.GP5, board.GP6))
sw_pins = (board.GP7, board.GP8)
sliders = [analogio.AnalogIn(pin) for pin in slider_pins]
encoders = [rotaryio.IncrementalEncoder(a, b) for a, b in enc_pins]
switches = []
last_positions = [0, 0]

for pin in sw_pins:
    sw = DigitalInOut(pin)
    sw.direction = Direction.INPUT
    sw.pull = Pull.UP
    switches.append(sw)


def sample_sliders():
    # scale 16-bit analog values down to 10-bit range
    write_i16(packet, 1, sliders[0].value >> 6)
    write_i16(packet, 3, sliders[1].value >> 6)
    write_i16(packet, 5, sliders[2].value >> 6)


def sample_flags():
    flags = 0
    for idx, encoder in enumerate(encoders):
        pos = encoder.position
        delta = pos - last_positions[idx]
        last_positions[idx] = pos
        if delta > 0:
            flags |= 0x10 if idx == 0 else 0x40
        elif delta < 0:
            flags |= 0x20 if idx == 0 else 0x80
        if not switches[idx].value:
            flags |= 1 << idx
    packet[7] = flags


with i2ctarget.I2CTarget(board.GP27, board.GP26, (0x32,)) as device:
    while True:
        sample_sliders()
        sample_flags()

        r = device.request()
        if r:
            with r:
                if r.is_read:
                    r.write(packet)
