from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line
from datetime import datetime


class Martingale(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.root = BoxLayout(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(8)
        )
        self.add_widget(self.root)

        # ================= INPUT =================
        self.input = TextInput(
            hint_text="PASTE SIGNAL VIP",
            size_hint_y=None,
            height=dp(100)
        )

        self.enter_btn = Button(
            text="ENTER SIGNAL",
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.8, 1, 1)
        )

        self.title = Label(
            text="WAITING SIGNAL...",
            size_hint_y=None,
            height=dp(40)
        )

        self.clear_btn = Button(
            text="HAPUS ALL",
            size_hint_y=None,
            height=dp(50),
            background_color=(1, 0, 0, 1)
        )

        self.enter_btn.bind(on_press=self.process_signal)
        self.clear_btn.bind(on_press=self.reset_all)

        # ================= SCROLL DATA =================
        self.scroll = ScrollView()

        self.box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(6)
        )
        self.box.bind(minimum_height=self.box.setter("height"))

        self.scroll.add_widget(self.box)

        # ================= LAYOUT URUTAN =================
        self.root.add_widget(self.input)
        self.root.add_widget(self.enter_btn)
        self.root.add_widget(self.title)
        self.root.add_widget(self.clear_btn)
        self.root.add_widget(self.scroll)

    # ================= PROCESS INPUT =================
    def process_signal(self, instance):

        raw = self.input.text.upper().strip()
        self.input.text = ""

        self.title.text = "SIGNAL VIP STC | " + datetime.now().strftime("%d %B %Y")

        tokens = raw.split()

        i = 0
        while i < len(tokens) - 1:

            time = tokens[i]
            sig = tokens[i + 1]

            if ":" in time and sig in ["B", "S"]:
                self.add_row(time, sig)
                i += 2
            else:
                i += 1

    # ================= ADD ROW =================
    def add_row(self, time, signal):

        row = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(6)
        )

        # border neon
        with row.canvas.after:
            Color(0, 0.8, 1, 1)
            line = Line(
                rounded_rectangle=(0, 0, 0, 0, dp(8)),
                width=1.2
            )

        def update(*a):
            line.rounded_rectangle = (row.x, row.y, row.width, row.height, dp(8))

        row.bind(pos=update, size=update)

        # TIME
        row.add_widget(Label(text=time, size_hint_x=0.3))

        # SIGNAL
        row.add_widget(Label(text=signal, size_hint_x=0.2))

        # COLOR BOX
        color_box = BoxLayout(size_hint_x=0.2)

        def draw(inst, *a):
            inst.canvas.before.clear()
            with inst.canvas.before:
                if signal == "B":
                    Color(0, 1, 0, 1)
                else:
                    Color(1, 0, 0, 1)
                Rectangle(pos=inst.pos, size=inst.size)

        color_box.bind(pos=draw, size=draw)

        row.add_widget(color_box)

        # ================= MARTINGALE BUTTON =================
        btn = Button(
            text="ON",
            size_hint_x=0.3,
            background_color=(0, 0.8, 1, 1)
        )

        def cycle(inst):
            if inst.text == "ON":
                inst.text = "K1"
            elif inst.text == "K1":
                inst.text = "K2"
            elif inst.text == "K2":
                inst.text = "K3"
            elif inst.text == "K3":
                inst.text = "WIN"
            elif inst.text == "WIN":
                inst.text = "LOSS"
            else:
                inst.text = "ON"

        btn.bind(on_press=cycle)

        row.add_widget(btn)

        self.box.add_widget(row)

    # ================= RESET =================
    def reset_all(self, instance):

        self.box.clear_widgets()
        self.input.text = ""
        self.title.text = "WAITING SIGNAL..."
