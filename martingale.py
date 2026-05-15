from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from datetime import datetime


class Martingale(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.root = BoxLayout(
            orientation="vertical",
            padding=dp(6),
            spacing=dp(6)
        )
        self.add_widget(self.root)

        # ======================
        # INPUT AREA
        # ======================
        self.input = TextInput(
            hint_text="PASTE SIGNAL VIP",
            size_hint_y=None,
            height=dp(120)
        )

        self.enter_btn = Button(
            text="ENTER SIGNAL",
            size_hint_y=None,
            height=dp(55),
            background_normal="",
            background_color=(0, 0.8, 1, 1),
            color=(0, 0, 0, 1)
        )

        self.clear_btn = Button(
            text="HAPUS ALL",
            size_hint_y=None,
            height=dp(55),
            background_normal="",
            background_color=(1, 0, 0, 1),
            color=(1, 1, 1, 1)
        )

        self.enter_btn.bind(on_press=self.process_signal)
        self.clear_btn.bind(on_press=self.reset_all)

        self.root.add_widget(self.input)
        self.root.add_widget(self.enter_btn)
        self.root.add_widget(self.clear_btn)

        # ======================
        # TITLE
        # ======================
        self.title = Label(
            text="WAITING SIGNAL...",
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            bold=True
        )
        self.root.add_widget(self.title)

        # ======================
        # HEADER TABLE
        # ======================
        header = BoxLayout(size_hint_y=None, height=dp(35))

        header.add_widget(Label(text="TIME"))
        header.add_widget(Label(text="B/S"))
        header.add_widget(Label(text="COLOR"))
        header.add_widget(Label(text="ACTION"))

        self.root.add_widget(header)

        # ======================
        # SCROLL TABLE
        # ======================
        self.scroll = ScrollView()

        self.box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(2)
        )
        self.box.bind(minimum_height=self.box.setter("height"))

        self.scroll.add_widget(self.box)
        self.root.add_widget(self.scroll)

    # ======================
    # PROCESS INPUT
    # ======================
    def process_signal(self, instance):

        raw = self.input.text.upper().strip()
        self.input.text = ""

        self.input.height = 0
        self.enter_btn.height = 0

        self.title.text = "SIGNAL VIP STC | " + datetime.now().strftime("%d %b %Y")

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

    # ======================
    # ADD ROW (FIX CLEAN UI)
    # ======================
    def add_row(self, time, signal):

        row = BoxLayout(
            size_hint_y=None,
            height=dp(35)
        )

        # BUTTON ON / K1 / K2 / WIN / LOSS
        btn = Button(
            text="ON",
            background_normal="",
            background_color=(1, 1, 1, 1),  # putih
            color=(0, 0, 0, 1)              # hitam
        )

        def cycle(inst):

            if inst.text == "ON":
                inst.text = "K1"
            elif inst.text == "K1":
                inst.text = "K2"
            elif inst.text == "K2":
                inst.text = "K3"
            elif inst.text == "K3":
                inst.text = "K4"
            elif inst.text == "K4":
                inst.text = "K5"
            elif inst.text == "K5":
                inst.text = "WIN"
            elif inst.text == "WIN":
                inst.text = "LOSS"
            else:
                inst.text = "ON"

        btn.bind(on_press=cycle)

        # ======================
        # FIX COLUMN WIDTH BIAR TIDAK BERANTAKAN
        # ======================

        # TIME
        row.add_widget(Label(
            text=time,
            size_hint_x=0.25
        ))

        # B / S (WARNA KIVY, BUKAN EMOJI)
        row.add_widget(Label(
            text=signal,
            size_hint_x=0.15,
            color=(0, 1, 0, 1) if signal == "B" else (1, 0, 0, 1)
        ))

        # COLOR INFO (TEXT SAJA, TANPA STICKER)
        row.add_widget(Label(
            text="GREEN" if signal == "B" else "RED",
            size_hint_x=0.2
        ))

        # BUTTON
        row.add_widget(btn)

        self.box.add_widget(row)

    # ======================
    # RESET
    # ======================
    def reset_all(self, instance):

        self.box.clear_widgets()

        self.input.height = dp(120)
        self.enter_btn.height = dp(55)

        self.input.text = ""
        self.title.text = "WAITING SIGNAL..."
