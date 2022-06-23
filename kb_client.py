import dbus
import sys
import evdev
import kb_client_keymap as keymap
from time import sleep

HID_DBUS = 'org.yaptb.btkbservice'
HID_SRVC = '/org/yaptb/btkbservice'


class Kbrd:
    """
    Take the events from a physically attached keyboard and send the
    HID messages to the keyboard D-Bus server.
    """
    def __init__(self, event_ids):
        self.target_length = 6
        self.mod_keys = 0b00000000
        self.pressed_keys = []
        self.have_kb = False
        self.dx = 0
        self.dy = 0
        self.button = 0
        self.devs = []
        self.bus = dbus.SystemBus()
        self.btkobject = self.bus.get_object(HID_DBUS,
                                             HID_SRVC)
        self.btk_service = dbus.Interface(self.btkobject,
                                          HID_DBUS)
        self.wait_for_keyboard(event_ids)

    def wait_for_keyboard(self, event_ids):
        """
        Connect to the input event file for the keyboard.
        Can take a parameter of an integer that gets appended to the end of
        /dev/input/event
        :param event_id: Optional parameter if the keyboard is not event0
        """
        while not self.have_kb:
            try:
                # try and get a keyboard - should always be event0 as
                # we're only plugging one thing in
                for i in event_ids:
                    self.devs.append(evdev.InputDevice('/dev/input/event{}'.format(i)))
                self.have_kb = True
            except OSError:
                print('Keyboard not found, waiting 3 seconds and retrying')
                sleep(3)
            print('found a keyboard')

    def update_mod_keys(self, mod_key, value):
        """
        Which modifier keys are active is stored in an 8 bit number.
        Each bit represents a different key. This method takes which bit
        and its new value as input
        :param mod_key: The value of the bit to be updated with new value
        :param value: Binary 1 or 0 depending if pressed or released
        """
        bit_mask = 1 << (7-mod_key)
        if value: # set bit
            self.mod_keys |= bit_mask
        else: # clear bit
            self.mod_keys &= ~bit_mask

    def update_keys(self, norm_key, value):
        if value < 1:
            self.pressed_keys.remove(norm_key)
        elif norm_key not in self.pressed_keys:
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
        print('Listening...')
        while True:
            event = None
            for dev in self.devs:
                event = dev.read_one()
                if event != None:
                    break
            if event == None:
                    continue
            # only bother if we hit a key and its an up or down event
            if event.type == evdev.ecodes.EV_KEY and event.value < 2:
                if event.code == evdev.ecodes.BTN_LEFT:
                    print('Button sent...')
                    self.button = event.value
                    self.send_mouse()
                    continue
                print('Keys sent...')
                key_str = evdev.ecodes.KEY[event.code]
                mod_key = keymap.modkey(key_str)
                if mod_key > -1:
                    self.update_mod_keys(mod_key, event.value)
                else:
                    self.update_keys(keymap.convert(key_str), event.value)
                self.send_keys()
            if event.type == evdev.ecodes.EV_REL:
                print('Mouse sent...')
                if event.code == evdev.ecodes.REL_X:
                    self.dx = int((event.value if event.value >= 0 else 512 + event.value) / 512.0 * 256)
                if event.code == evdev.ecodes.REL_Y:
                    self.dy = int((event.value if event.value >= 0 else 512 + event.value) / 512.0 * 256)
                self.send_mouse()


if __name__ == '__main__':
    print('Setting up keyboard')
    if len(sys.argv) < 2:
        print("Invalid args");
        sys.exit(1)
    kb = Kbrd(sys.argv[1:])

    print('starting event loop')
    kb.event_loop()
