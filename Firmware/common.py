PACKET_LEN = 8
MACROPAD_ADDR = 0x31
SLIDERPAD_ADDR = 0x32
MATRIX_ADDR = 0x33



def clamp(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value


def write_i16(buf, idx, value):
    if value < 0:
        value = (1 << 16) + value
    buf[idx] = value & 0xFF
    buf[idx + 1] = (value >> 8) & 0xFF


def read_i16(buf, idx):
    value = buf[idx] | (buf[idx + 1] << 8)
    if value & 0x8000:
        value -= 1 << 16
    return value


def unpack_packet(buf):
    return {
        'id': buf[0],
        'value0': read_i16(buf, 1),
        'value1': read_i16(buf, 3),
        'value2': read_i16(buf, 5),
        'flags': buf[7],
    }


def make_packet(module_id):
    packet = bytearray(PACKET_LEN)
    packet[0] = module_id
    return packet