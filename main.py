import os

LOG_PATHS = [
    "/data/data/org.ankitxt.ankitxt/files/ankitxt_boot.txt",
]

def _log(msg):
    for p in LOG_PATHS:
        try:
            d = os.path.dirname(p)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
            with open(p, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except Exception:
            pass

_log("step0: script start")

from kivy.app import App
from kivy.uix.label import Label
_log("step1: kivy imported")

class TestApp(App):
    def build(self):
        _log("step2: build() called")
        return Label(text="Hello AnkiTXT")

if __name__ == "__main__":
    _log("step3: about to run")
    TestApp().run()
