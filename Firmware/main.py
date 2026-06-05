import board
import busio
import neopixel
import supervisor
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.modules.encoder import EncoderHandler
from kmk.modules.layers import Layers
from kmk.scanners import DiodeOrientation
from common import MACROPAD_ADDR, SLIDERPAD_ADDR, MATRIX_ADDR, PACKET_LEN, unpack_packet, clamp

keyboard = KMKKeyboard()
keyboard.col_pins = (
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    board.GP12,
    board.GP13,
    board.GP14,
    board.GP15,
    board.GP16,
    board.GP17,
    board.GP18,
    board.GP19,
    board.GP20,
)
keyboard.row_pins = (board.GP2, board.GP3, board.GP4, board.GP5, board.GP6)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

layers = Layers()
keyboard.modules.append(layers)

encoder_handler = EncoderHandler()
encoder_handler.pins = ((board.GP21, board.GP22, board.GP26),)
encoder_handler.map = (
    ((KC.VOLD, KC.VOLU, KC.MUTE),),
    ((KC.LEFT, KC.RIGHT, KC.MPLY),),
)
keyboard.modules.append(encoder_handler)

FN = KC.MO(1)
keyboard.keymap = [
    [
        KC.N1, KC.N2, KC.N3, KC.N4, KC.N5, KC.N6, KC.N7, KC.N8, KC.N9, KC.N0, KC.MINS, KC.EQL, KC.BSPC, KC.NO,
        KC.TAB, KC.Q, KC.W, KC.E, KC.R, KC.T, KC.Y, KC.U, KC.I, KC.O, KC.P, KC.LBRC, KC.RBRC, KC.BSLS,
        KC.ESC, KC.A, KC.S, KC.D, KC.F, KC.G, KC.H, KC.J, KC.K, KC.L, KC.SCLN, KC.QUOT, KC.ENT, KC.NO,
        KC.LSFT, KC.Z, KC.X, KC.C, KC.V, KC.B, KC.N, KC.M, KC.COMM, KC.DOT, KC.SLSH, KC.UP, KC.NO, KC.NO,
        KC.LCTL, KC.LGUI, KC.LALT, FN, KC.SPC, KC.SPC, KC.SPC, KC.SPC, KC.SPC, KC.LEFT, KC.DOWN, KC.RGHT, KC.NO, KC.NO,
    ],
    [
        KC.F1, KC.F2, KC.F3, KC.F4, KC.F5, KC.F6, KC.F7, KC.F8, KC.F9, KC.F10, KC.F11, KC.F12, KC.DEL, KC.NO,
        KC.TRNS, KC.RGB_TOG, KC.RGB_MOD, KC.RGB_HUI, KC.RGB_SAI, KC.RGB_VAI, KC.NO, KC.NO, KC.UP, KC.NO, KC.PSCR, KC.HOME, KC.END, KC.INS,
        KC.CAPS, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.LEFT, KC.DOWN, KC.RIGHT, KC.NO, KC.NO, KC.NO, KC.TRNS, KC.NO,
        KC.TRNS, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.PGUP, KC.NO, KC.NO,
        KC.TRNS, KC.TRNS, KC.TRNS, KC.TRNS, KC.TRNS, KC.TRNS, KC.TRNS, KC.TRNS, KC.TRNS, KC.HOME, KC.PGDN, KC.END, KC.NO, KC.NO,
    ],
]

i2c = busio.I2C(scl=board.GP1, sda=board.GP0, frequency=400000)
last_macropad_flags = 0
last_slider_flags = 0
last_slider_band = -1
anim_phase = 0
matrix_tx = bytearray(6)
matrix_tx[0] = 0xA5

macro_actions = {
    0: KC.LCTL(KC.C),
    1: KC.LCTL(KC.V),
    2: KC.LCTL(KC.X),
    3: KC.LCTL(KC.Z),
    4: KC.LCTL(KC.S),
    5: KC.LCTL(KC.P),
    6: KC.F13,
    7: KC.F14,
}


class ModuleState:
    def __init__(self):
        self.connected = False
        self.last_seen = 0


macropad_state = ModuleState()
sliderpad_state = ModuleState()
matrix_state = ModuleState()


def read_packet(addr):
    if not i2c.try_lock():
        return None
    raw = bytearray(PACKET_LEN)
    try:
        i2c.readfrom_into(addr, raw)
    except OSError:
        raw = None
    i2c.unlock()
    if raw is None:
        return None
    return unpack_packet(raw)


def write_matrix(mode, phase, status_bits, accent, level):
    if not i2c.try_lock():
        return
    matrix_tx[1] = mode & 0xFF
    matrix_tx[2] = phase & 0xFF
    matrix_tx[3] = status_bits & 0xFF
    matrix_tx[4] = accent & 0xFF
    matrix_tx[5] = level & 0xFF
    try:
        i2c.writeto(MATRIX_ADDR, matrix_tx)
        note_module(matrix_state)
    except OSError:
        pass
    i2c.unlock()


def tap(code):
    keyboard.tap_key(code)


def note_module(module_state):
    module_state.connected = True
    module_state.last_seen = supervisor.ticks_ms()


def clear_stale_modules():
    now = supervisor.ticks_ms()
    if now - macropad_state.last_seen > 1000:
        macropad_state.connected = False
    if now - sliderpad_state.last_seen > 1000:
        sliderpad_state.connected = False
    if now - matrix_state.last_seen > 1000:
        matrix_state.connected = False


def handle_macropad(packet):
    global last_macropad_flags
    note_module(macropad_state)
    rising = packet['flags'] & ~last_macropad_flags
    last_macropad_flags = packet['flags']
    for bit, keycode in macro_actions.items():
        if rising & (1 << bit):
            tap(keycode)


slider_map = {
    0: KC.MPRV,
    1: None,
    2: KC.MPLY,
    3: KC.MNXT,
}


def slider_band(value):
    return clamp(value // 1024, 0, 3)


def handle_sliderpad(packet):
    global last_slider_flags, last_slider_band
    note_module(sliderpad_state)
    changed = packet['flags'] ^ last_slider_flags
    pressed = packet['flags']
    last_slider_flags = packet['flags']

    if changed & 0x01 and pressed & 0x01:
        tap(KC.MPLY)
    if changed & 0x02 and pressed & 0x02:
        tap(KC.MNXT)
    if changed & 0x10:
        tap(KC.VOLU)
    if changed & 0x20:
        tap(KC.VOLD)
    if changed & 0x40:
        tap(KC.RIGHT)
    if changed & 0x80:
        tap(KC.LEFT)

    band = slider_band(packet['value0'])
    if band != last_slider_band:
        last_slider_band = band
        action = slider_map.get(band)
        if action is not None:
            tap(action)


def update_matrix_module():
    # mode 1 for default layer, mode 2 for function layer
    mode = 1 if keyboard.active_layers[0] == 0 else 2
    status_bits = 0
    if macropad_state.connected:
        status_bits |= 0x01
    if sliderpad_state.connected:
        status_bits |= 0x02
    if matrix_state.connected:
        status_bits |= 0x04
    accent = last_slider_band if last_slider_band >= 0 else 0
    write_matrix(mode, anim_phase, status_bits, accent, 24)


def animate_matrix():
    global anim_phase
    anim_phase = (anim_phase + 1) & 0xFF
    update_matrix_module()


def after_matrix_scan(_):
    packet = read_packet(MACROPAD_ADDR)
    if packet and packet['id'] == 1:
        handle_macropad(packet)

    packet = read_packet(SLIDERPAD_ADDR)
    if packet and packet['id'] == 2:
        handle_sliderpad(packet)

    clear_stale_modules()

    if supervisor.ticks_ms() % 24 < 4:
        animate_matrix()


keyboard.after_matrix_scan = after_matrix_scan
keyboard.go()