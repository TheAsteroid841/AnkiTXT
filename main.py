# -*- coding: utf-8 -*-
import sys

try:
    with open("/sdcard/ankitxt_boot.txt", "w") as f:
        f.write("step1: import start\n")
except Exception:
    pass

from kivy.app import App
from kivy.uix.label import Label

try:
    with open("/sdcard/ankitxt_boot.txt", "a") as f:
        f.write("step2: kivy imported\n")
except Exception:
    pass


class TestApp(App):
    def build(self):
        try:
            with open("/sdcard/ankitxt_boot.txt", "a") as f:
                f.write("step3: build called\n")
        except Exception:
            pass
        return Label(text="Hello AnkiTXT")


if __name__ == "__main__":
    try:
        with open("/sdcard/ankitxt_boot.txt", "a") as f:
            f.write("step4: run\n")
    except Exception:
        pass
    TestApp().run()
