import dbus
import keymap
from time import sleep

import os
import curses

HID_DBUS = 'org.yaptb.btkbservice'
HID_SRVC = '/org/yaptb/btkbservice'


class Kbrd:
    """
    Take the events from a physically attached keyboard and send the
    HID messages to the keyboard D-Bus server.
    """
    def __init__(self):
        self.target_length = 6
        self.mod_keys = 0b00000000
        self.pressed_keys = []
        self.have_kb = False
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.button = 0
        self.dev = None
        self.bus = dbus.SystemBus()
        self.btkobject = self.bus.get_object(HID_DBUS,
                                             HID_SRVC)
        self.btk_service = dbus.Interface(self.btkobject,
                                          HID_DBUS)

        os.environ['TERM'] = 'xterm-1003'
        self.screen = curses.initscr()
        self.screen.keypad(1)
        curses.curs_set(0)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.flushinp()
        curses.noecho()
        self.screen.clear()

    def update_mod_keys(self, mod_key):
        """
        Which modifier keys are active is stored in an 8 bit number.
        Each bit represents a different key. This method takes which bit
        and its new value as input
        :param mod_key: The value of the bit to be updated with new value
        :param value: Binary 1 or 0 depending if pressed or released
        """
        bit_mask = 1 << (7-mod_key)
        if mod_key != 0: # set bit
            self.mod_keys |= bit_mask
        else: # clear bit
            self.mod_keys = 0

    def update_keys(self, norm_key):
        if norm_key not in self.pressed_keys:
            self.pressed_keys.insert(0, norm_key)

        len_delta = self.target_length - len(self.pressed_keys)
        if len_delta < 0:
            self.pressed_keys = self.pressed_keys[:len_delta]
        elif len_delta > 0:
            self.pressed_keys.extend([0] * len_delta)

    @property
    def state(self):
        """
        property with the HID message to send for the current keys pressed
        on the keyboards
        :return: bytes of HID message
        """
        return [0xA1, 0x01, self.mod_keys, 0, *self.pressed_keys]

    def clean_axis_value(self, value):
        value = value if value > -127 else -127
        value = value if value < 127 else 127
        value = value if value >= 0 else 256 + value
        return value

    def update_mouse(self, x, y, button):
        self.dx = self.clean_axis_value((x - self.x) * 10)
        self.dy = self.clean_axis_value((y - self.y) * 25)
        self.x = x
        self.y = y
        self.button = 1 if button == curses.BUTTON1_PRESSED or button == curses.BUTTON1_CLICKED else 0 if button != 0x10000000 else self.button

    @property
    def mouse_state(self):
        """
        property with the HID message to send for the current keys pressed
        on the keyboards
        :return: bytes of HID message
        """
        return [0xA1, 0x03, self.button, self.dx, self.dy]

    def send_keys(self):
        self.btk_service.send_keys(self.state)

    def send_mouse(self):
        self.btk_service.send_keys(self.mouse_state)

    def event_loop(self):
        """
        Loop to check for keyboard events and send HID message
        over D-Bus keyboard service when they happen
        """
        while True:
            self.pressed_keys = []
            self.update_keys(0)
            self.update_mod_keys(0)
            self.send_keys()
            key = self.screen.getch()
            ch = chr(key)
            self.screen.clear()
            self.screen.addstr(0, 0, 'key: {}'.format(key))
            if key == curses.KEY_MOUSE:
                _, x, y, _, button = curses.getmouse()
                self.screen.addstr(1, 0, 'x, y, button = {}, {}, {}'.format(x, y, button))
                self.update_mouse(x, y, button)
                self.screen.addstr(2, 0, 'dx, dy, button = {}, {}, {}'.format(self.dx if self.dx < 127 else self.dx - 256, self.dy if self.dy < 127 else self.dy - 256, self.button))
                self.send_mouse()
                if button == 4:
                    self.button = 0
                    self.send_mouse()
            elif key == 276: #F12
                self.btk_service.switch_device()
            else:
                mod_key = keymap.modkey(ch)
                if mod_key > -1:
                    self.update_mod_keys(mod_key)
                    if ch >= 'A' and ch <= 'Z':
                        ch = ch.lower()
                self.update_keys(keymap.convert(ch))
                self.send_keys()

        curses.endwin()
        curses.flushinp()

if __name__ == '__main__':
    print('Setting up keyboard')
    kb = Kbrd()

    print('starting event loop')
    kb.event_loop()
