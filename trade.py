import webbrowser
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout


class Trade(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        layout = BoxLayout(orientation="vertical")

        btn = Button(
            text="OPEN STC BROKER",
            font_size=20
        )

        btn.bind(on_press=self.open_site)

        layout.add_widget(btn)
        self.add_widget(layout)

    def open_site(self, instance):
        webbrowser.open("https://stcbroker.id")
