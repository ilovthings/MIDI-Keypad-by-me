# I didnt have enough money for some things, like the leds or key, so thats why they are missing in the code.
#I also vibe code this🤑, I dont know ANYTHING about coding python 4 an MCU, and the guide did it also! I fell like i didnt do anything wrong.
import keypad
import touchio
import busio
from microcontroller import pin

from kmk.scanners import Scanner
from kmk.extensions.media_keys import MediaKeys
from kmk.extensions.display import Display, TextEntry
from kmk.extensions.display.ssd1306 import SSD1306
from kmk.keys import KC
from kmk.kmk_keyboard import KMKKeyboard
from kmk.modules.encoder import EncoderHandler
from kmk.modules.layers import Layers
from kmk.modules.midi import MidiKeys

class TouchScanner(Scanner):
    def __init__(self, pins):
        self.pads = [touchio.TouchIn(p) for p in pins]
        self.pressed = [False] * len(pins)

    @property
    def key_count(self):
        return len(self.pads)

    def scan_for_changes(self):
        for i, pad in enumerate(self.pads):
            touched = pad.value

            if touched != self.pressed[i]:
                self.pressed[i] = touched
                return keypad.Event(i + self.offset, touched)


keyboard = KMKKeyboard()

layers = Layers()
midi = MidiKeys()
media_keys = MediaKeys()

keyboard.matrix = [
    TouchScanner([
        pin.GPIO13,
        pin.GPIO12,
        pin.GPIO11,
        pin.GPIO10,
        pin.GPIO9,
        pin.GPIO8,
    ]),
]


#two mode for d pads

keyboard.keymap = [

    # group 1, piano notes
    [
        KC.MIDI_NOTE(60), 
        KC.MIDI_NOTE(62), 
        KC.MIDI_NOTE(64), 
        KC.MIDI_NOTE(65),  
        KC.MIDI_NOTE(67),
        KC.MIDI_NOTE(69),  
    ],

    
    # group 2, drumps hits
    [
        KC.MIDI_NOTE(36, channel=9),  
        KC.MIDI_NOTE(38, channel=9),  
        KC.MIDI_NOTE(42, channel=9),  
        KC.MIDI_NOTE(46, channel=9),  
        KC.MIDI_NOTE(50, channel=9), 
        KC.MIDI_NOTE(49, channel=9),  
    ],
]


#oled part

i2c_bus = busio.I2C(
    pin.GPIO6,
    pin.GPIO5,
)

oled_driver = SSD1306(
    i2c=i2c_bus,
    device_address=0x3C,
)


#this is for show volume
volume_state = {"level": 50}

mode_notes = TextEntry(
    text="Mode: NOTES",
    x=0,
    y=0,
    layer=0,
)

mode_drums = TextEntry(
    text="Mode: DRUMS",
    x=0,
    y=0,
    layer=1,
)

volume_text = TextEntry(
    text="Volume ~50%",
    x=0,
    y=11,
)

volume_bar = TextEntry(
    text="[#####-----]",
    x=0,
    y=22,
)


display = Display(
    display=oled_driver,
    entries=[
        mode_notes,
        mode_drums,
        volume_text,
        volume_bar,
    ],
    width=128,
    height=32,
    brightness=0.8,

   
    dim_time=0,
    off_time=0,
)


#this is for control volume

class VolumeEncoder(EncoderHandler):

    def on_move_do(self, keyboard, encoder_id, state):

        # Preserve KMK's normal volume-up/down behavior.
        super().on_move_do(keyboard, encoder_id, state)

        direction = state["direction"]


        if direction == -1:
            volume_state["level"] = max(
                0,
                volume_state["level"] - 2,
            )

        elif direction == 1:
            volume_state["level"] = min(
                100,
                volume_state["level"] + 2,
            )

    
        level = volume_state["level"]
        volume_text.text = "Volume ~{}%".format(level)

    
        filled = level // 10

        volume_bar.text = (
            "[" +
            "#" * filled +
            "-" * (10 - filled) +
            "]"
        )

   
        display.render(keyboard.active_layers[0])


encoder = VolumeEncoder()

encoder.pins = (
    (pin.GPIO1, pin.GPIO2, pin.GPIO4),
)

encoder.map = [
    ((KC.VOLD, KC.VOLU, KC.TG(1)),),
    ((KC.VOLD, KC.VOLU, KC.TG(1)),),
]

keyboard.modules = [
    layers,
    midi,
    encoder,
]

keyboard.extensions = [
    media_keys,
    display,
]


#begin

if __name__ == "__main__":
    keyboard.go()
