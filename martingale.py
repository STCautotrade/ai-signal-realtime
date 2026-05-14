from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class Martingale(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.add_widget(self.layout)

        # TITLE
        self.title = Label(
            text="MARTINGALE SYSTEM",
            font_size=20,
            size_hint_y=None,
            height=50
        )

        self.layout.add_widget(self.title)

        # INFO
        self.info = Label(
            text="INPUT SIGNAL AKAN MASUK DI SINI",
            font_size=16
        )

        self.layout.add_widget(self.info)
