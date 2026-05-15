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

        # ======================
        # INPUT + ENTER (AWAL ATAS)
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

        self.enter_btn.bind(on_press=self.process_signal)

        # ======================
        # JUDUL
        # ======================
        self.title = Label(
            text="WAITING SIGNAL...",
            size_hint_y=None,
            height=dp(45),
            bold=True
        )

        # ======================
        # HAPUS ALL
        # ======================
        self.clear_btn = Button(
            text="HAPUS ALL",
            size_hint_y=None,
            height=dp(55),
            background_normal="",
            background_color=(1, 0, 0, 1),
            color=(1, 1, 1, 1)
        )

        self.clear_btn.bind(on_press=self.reset_all)

        # ======================
        # SCROLL DATA
        # ======================
        self.scroll = ScrollView()

        self.box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8)
        )
        self.box.bind(minimum_height=self.box.setter("height"))

        self.scroll.add_widget(self.box)

        # ======================
        # ADD ORDER (AWAL)
        # ======================
        self.root.add_widget(self.input)
        self.root.add_widget(self.enter_btn)
        self.root.add_widget(self.title)
        self.root.add_widget(self.clear_btn)
        self.root.add_widget(self.scroll)

    # ======================
    # MOVE INPUT KE BAWAH
    # ======================
    def move_input_to_bottom(self):

        self.root.remove_widget(self.input)
        self.root.remove_widget(self.enter_btn)

        self.root.add_widget(self.input)
        self.root.add_widget(self.enter_btn)

    # ======================
    # PROCESS SIGNAL
    # ======================
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

        # 🔥 PINDAHKAN INPUT KE BAWAH SETELAH INPUT
        self.move_input_to_bottom()

    # ======================
    # ADD ROW
    # ======================
    def add_row(self, time, signal):

        row = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(6),
            padding=(dp(4), dp(4))
        )

        with row.canvas.after:
            Color(0, 0.8, 1, 1)
            line = Line(
                rounded_rectangle=(0, 0, 0, 0, dp(8)),
                width=1.2
            )

        def update_line(inst, *args):
            line.rounded_rectangle = (
                inst.x,
                inst.y,
                inst.width,
                inst.height,
                dp(8)
            )

        row.bind(pos=update_line, size=update_line)

        row.add_widget(Label(text=time, size_hint_x=0.30))
        row.add_widget(Label(text=signal, size_hint_x=0.15))

        color_box = BoxLayout(size_hint_x=0.18)

        def draw(inst, *args):
            inst.canvas.before.clear()
            with inst.canvas.before:
                if signal == "B":
                    Color(0, 1, 0, 1)
                else:
                    Color(1, 0, 0, 1)
                Rectangle(pos=inst.pos, size=inst.size)

        color_box.bind(pos=draw, size=draw)

        row.add_widget(color_box)

        self.box.add_widget(row)

    # ======================
    # RESET ALL (BALIK KE AWAL)
    # ======================
    def reset_all(self, instance):

        self.box.clear_widgets()

        # 🔥 BALIKIN INPUT KE ATAS
        self.root.clear_widgets()

        self.root.add_widget(self.input)
        self.root.add_widget(self.enter_btn)
        self.root.add_widget(self.title)
        self.root.add_widget(self.clear_btn)
        self.root.add_widget(self.scroll)

        self.input.text = ""
        self.title.text = "WAITING SIGNAL..."
