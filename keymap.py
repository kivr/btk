#
# www.linuxuser.co.uk/tutorials/emulate-a-bluetooth-keyboard-with-the-raspberry-pi
#
#
#
# Convert value returned from Linux event device ("evdev") to a HID code.
# This is reverse of what's actually hardcoded in the kernel.
#
# Lubomir Rintel <lkundrak@v3.sk>
# License: GPL
#
# Ported to a Python module by Liam Fraser.
#

import curses

keytable = {
    "KEY_RESERVED": 0,
    27: 41, #ESC
    "1": 30,
    "2": 31,
    "3": 32,
    "4": 33,
    "5": 34,
    "6": 35,
    "7": 36,
    "8": 37,
    "9": 38,
    "0": 39,
    "-": 45,
    "=": 46,
    chr(curses.KEY_BACKSPACE): 42,
    "\t": 43,
    "q": 20,
    "w": 26,
    "e": 8,
    "r": 21,
    "t": 23,
    "y": 28,
    "u": 24,
    "i": 12,
    "o": 18,
    "p": 19,
    "[": 47,
    "]": 48,
    "\n": 40,
    "KEY_LEFTCTRL": 224,
    "a": 4,
    "s": 22,
    "d": 7,
    "f": 9,
    "g": 10,
    "h": 11,
    "j": 13,
    "k": 14,
    "l": 15,
    ";": 51,
    "'": 52,
    "KEY_GRAVE": 53,
    "KEY_LEFTSHIFT": 225,
    "\\": 50,
    "z": 29,
    "x": 27,
    "c": 6,
    "v": 25,
    "b": 5,
    "n": 17,
    "m": 16,
    ",": 54,
    ".": 55,
    "/": 56,
    "KEY_RIGHTSHIFT": 229,
    "KEY_KPASTERISK": 85,
    "KEY_LEFTALT": 226,
    " ": 44,
    "KEY_CAPSLOCK": 57,
    "KEY_F1": 58,
    "KEY_F2": 59,
    "KEY_F3": 60,
    "KEY_F4": 61,
    "KEY_F5": 62,
    "KEY_F6": 63,
    "KEY_F7": 64,
    "KEY_F8": 65,
    "KEY_F9": 66,
    "KEY_F10": 67,
    "KEY_NUMLOCK": 83,
    "KEY_SCROLLLOCK": 71,
    "KEY_KP7": 95,
    "KEY_KP8": 96,
    "KEY_KP9": 97,
    "KEY_KPMINUS": 86,
    "KEY_KP4": 92,
    "KEY_KP5": 93,
    "KEY_KP6": 94,
    "KEY_KPPLUS": 87,
    "KEY_KP1": 89,
    "KEY_KP2": 90,
    "KEY_KP3": 91,
    "KEY_KP0": 98,
    "KEY_KPDOT": 99,
    "KEY_ZENKAKUHANKAKU": 148,
    "KEY_102ND": 100,
    "KEY_F11": 68,
    "KEY_F12": 69,
    "KEY_RO": 135,
    "KEY_KATAKANA": 146,
    "KEY_HIRAGANA": 147,
    "KEY_HENKAN": 138,
    "KEY_KATAKANAHIRAGANA": 136,
    "KEY_MUHENKAN": 139,
    "KEY_KPJPCOMMA": 140,
    "KEY_KPENTER": 88,
    "KEY_RIGHTCTRL": 228,
    "KEY_KPSLASH": 84,
    "KEY_SYSRQ": 70,
    "KEY_RIGHTALT": 230,
    chr(curses.KEY_HOME): 74,
    chr(curses.KEY_UP): 82,
    "KEY_PAGEUP": 75,
    chr(curses.KEY_LEFT): 80,
    chr(curses.KEY_RIGHT): 79,
    chr(curses.KEY_END): 77,
    chr(curses.KEY_DOWN): 81,
    "KEY_PAGEDOWN": 78,
    "KEY_INSERT": 73,
    "KEY_DELETE": 76,
    "KEY_MUTE": 239,
    "KEY_VOLUMEDOWN": 238,
    "KEY_VOLUMEUP": 237,
    "KEY_POWER": 102,
    "KEY_KPEQUAL": 103,
    "KEY_PAUSE": 72,
    "KEY_KPCOMMA": 133,
    "KEY_HANGEUL": 144,
    "KEY_HANJA": 145,
    "KEY_YEN": 137,
    "KEY_LEFTMETA": 227,
    "KEY_RIGHTMETA": 231,
    "KEY_COMPOSE": 101,
    "KEY_STOP": 243,
    "KEY_AGAIN": 121,
    "KEY_PROPS": 118,
    "KEY_UNDO": 122,
    "KEY_FRONT": 119,
    "KEY_COPY": 124,
    "KEY_OPEN": 116,
    "KEY_PASTE": 125,
    "KEY_FIND": 244,
    "KEY_CUT": 123,
    "KEY_HELP": 117,
    "KEY_CALC": 251,
    "KEY_SLEEP": 248,
    "KEY_WWW": 240,
    "KEY_COFFEE": 249,
    "KEY_BACK": 241,
    "KEY_FORWARD": 242,
    "KEY_EJECTCD": 236,
    "KEY_NEXTSONG": 235,
    "KEY_PLAYPAUSE": 232,
    "KEY_PREVIOUSSONG": 234,
    "KEY_STOPCD": 233,
    "KEY_REFRESH": 250,
    "KEY_EDIT": 247,
    "KEY_SCROLLUP": 245,
    "KEY_SCROLLDOWN": 246,
    "KEY_F13": 104,
    "KEY_F14": 105,
    "KEY_F15": 106,
    "KEY_F16": 107,
    "KEY_F17": 108,
    "KEY_F18": 109,
    "KEY_F19": 110,
    "KEY_F20": 111,
    "KEY_F21": 112,
    "KEY_F22": 113,
    "KEY_F23": 114,
    "KEY_F24": 115
}

# Map modifier keys to array element in the bit array
modkeys = {
    "KEY_RIGHTMETA": 0,
    "KEY_RIGHTALT": 1,
    "KEY_RIGHTSHIFT": 2,
    "KEY_RIGHTCTRL": 3,
    "KEY_LEFTMETA": 4,
    "KEY_LEFTALT": 5,
    "KEY_LEFTSHIFT": 6,
    "KEY_LEFTCTRL": 7
}

shiftconverttable = {
    "!": "1",
    "@": "2",
    "#": "3",
    "$": "4",
    "%": "5",
    "^": "6",
    "&": "7",
    "*": "8",
    "(": "9",
    ")": "0",
    ":": ";",
    "{": "[",
    "}": "]",
    "\"": "'",
    "?": "/",
    "_": "-",
    chr(curses.KEY_BTAB): "\t",
}

ctrlconverttable = {
    "\x01": "a",
    "\x04": "d",
    "\x0c": "l",
}

def convert(code):
    if code in shiftconverttable.keys():
        return keytable[shiftconverttable[code]]
    elif code in ctrlconverttable.keys():
        return keytable[ctrlconverttable[code]]
    return keytable[code] if code in keytable.keys() else 0


def modkey(code):
    if code >= 'A' and code <= 'Z' or code in shiftconverttable.keys():
        return modkeys["KEY_LEFTSHIFT"]
    elif code in ctrlconverttable.keys():
        return modkeys["KEY_LEFTCTRL"]
    else:
        return -1  # Return an invalid array element
