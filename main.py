
# main.py
from pathlib import Path
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import platform
from core import parse_txt, build_apkg, build_merged_apkg

TXT_DIR = Path("/sdcard/Download")


def ask_perms():
    if platform != "android":
        return
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
    except Exception:
        pass


class MainUI(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=dp(10),
                         spacing=dp(8), **kw)
        self.add_widget(Label(text="AnkiTXT", font_size="22sp", bold=True,
                              size_hint_y=None, height=dp(40)))
        self.add_widget(Button(text="刷新", size_hint_y=None, height=dp(44),
                               on_release=lambda *_: self.refresh()))
        self.scroll = ScrollView()
        self.box = BoxLayout(orientation="vertical",
                             size_hint_y=None, spacing=dp(6))
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        self.add_widget(self.scroll)
        self.add_widget(Button(text="全部合并为一个apkg",
                               size_hint_y=None, height=dp(52),
                               background_color=(0.2, 0.6, 1, 1),
                               on_release=lambda *_: self.do_all()))
        self.status = Label(text="就绪", size_hint_y=None, height=dp(60))
        self.add_widget(self.status)
        Clock.schedule_once(lambda *_: self.refresh(), 0.5)

    def list_txt(self):
        if not TXT_DIR.exists():
            return []
        return sorted(p for p in TXT_DIR.iterdir()
                      if p.is_file() and p.suffix.lower() == ".txt")

    def refresh(self):
        self.box.clear_widgets()
        files = self.list_txt()
        if not files:
            self.box.add_widget(Label(text="(无 txt 文件)",
                                      size_hint_y=None, height=dp(60)))
            self.status.text = f"目录 {TXT_DIR} 下无 txt"
            return
        for f in files:
            b = Button(text=f.name, size_hint_y=None, height=dp(48))
            b.bind(on_release=lambda _b, p=f: self.do_one(p))
            self.box.add_widget(b)
        self.status.text = f"共 {len(files)} 个文件"

    def do_one(self, path):
        try:
            text = path.read_text(encoding="utf-8")
            cards = parse_txt(text)
            if not cards:
                self.status.text = f"{path.name}: 无卡片"
                return
            out = path.with_suffix(".apkg")
            n = build_apkg(cards, str(out), path.stem)
            self.status.text = f"{path.name} -> {n} 张"
        except Exception as e:
            self.status.text = f"{path.name} 失败: {e}"

    def do_all(self):
        files = self.list_txt()
        if not files:
            self.status.text = "无可转换文件"
            return
        grouped = {}
        for f in files:
            try:
                cards = parse_txt(f.read_text(encoding="utf-8"))
                if cards:
                    grouped[f.stem] = cards
            except Exception:
                continue
        if not grouped:
            self.status.text = "全部解析失败"
            return
        parent = TXT_DIR.name or "AnkiTXT"
        out = TXT_DIR / f"{parent}.apkg"
        try:
            n = build_merged_apkg(grouped, parent, str(out))
            self.status.text = f"合并完成 {n} 张 -> {out.name}"
        except Exception as e:
            self.status.text = f"合并失败: {e}"


class AnkiTXTApp(App):
    def build(self):
        ask_perms()
        return MainUI()


if __name__ == "__main__":
    AnkiTXTApp().run()
