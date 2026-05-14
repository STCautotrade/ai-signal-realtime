from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from datetime import datetime


class Martingale(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.root = BoxLayout(orientation="vertical", padding=5, spacing=5)
        self.add_widget(self.root)

        self.rows = []

        # ======================
        # INPUT AREA
        # ======================
        self.input = TextInput(
            hint_text="PASTE SIGNAL VIP",
            size_hint_y=None,
            height=150
        )

        self.enter_btn = Button(
            text="ENTER SIGNAL",
            size_hint_y=None,
            height=50
        )

        self.clear_btn = Button(
            text="HAPUS ALL",
            size_hint_y=None,
            height=50,
            background_color=(1, 0, 0, 1)
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
            height=40
        )
        self.root.add_widget(self.title)

        # ======================
        # HEADER TABLE
        # ======================
        header = BoxLayout(size_hint_y=None, height=30)

        for h in ["TIME", "B/S", "STATUS", "ACTION"]:
            header.add_widget(Label(text=h))

        self.root.add_widget(header)

        # ======================
        # SCROLL AREA
        # ======================
        self.scroll = ScrollView()

        self.box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=2
        )

        self.box.bind(minimum_height=self.box.setter("height"))

        self.scroll.add_widget(self.box)
        self.root.add_widget(self.scroll)

    # ======================
    # PROCESS SIGNAL
    # ======================
    def process_signal(self, instance):

        raw = self.input.text.strip()
        self.input.text = ""

        # hide input UI
        self.input.height = 0
        self.enter_btn.height = 0

        self.title.text = "SIGNAL VIP STC | " + datetime.now().strftime("%d %b %Y")

        tokens = raw.split()

        i = 0
        while i < len(tokens) - 1:

            time = tokens[i]
            sig = tokens[i + 1].upper()

            if ":" in time and sig in ["B", "S"]:
                self.add_row(time, sig)
                i += 2
            else:
                i += 1

    # ======================
    # ADD ROW
    # ======================
    def add_row(self, time, signal):

        row = BoxLayout(size_hint_y=None, height=30)

        color = "🟩" if signal == "B" else "🟥"

        btn = Button(
            text="ON",
            background_color=(0, 0.4, 1, 1)
        )

        def cycle(instance):

            if instance.text == "ON":
                instance.text = "K1"
            elif instance.text == "K1":
                instance.text = "K2"
            elif instance.text == "K2":
                instance.text = "K3"
            elif instance.text == "K3":
                instance.text = "K4"
            elif instance.text == "K4":
                instance.text = "K5"
            elif instance.text == "K5":
                instance.text = "WIN"
            elif instance.text == "WIN":
                instance.text = "LOSS"
            else:
                instance.text = "ON"

        btn.bind(on_press=cycle)

        row.add_widget(Label(text=time))
        row.add_widget(Label(text=signal))
        row.add_widget(Label(text=color))
        row.add_widget(btn)

        self.box.add_widget(row)

    # ======================
    # RESET ALL (HAPUS ALL)
    # ======================
    def reset_all(self, instance):

        # clear data
        self.box.clear_widgets()
        self.rows.clear()

        # restore input UI
        self.input.height = 150
        self.enter_btn.height = 50

        self.input.text = ""

        self.title.text = "WAITING SIGNAL..."
