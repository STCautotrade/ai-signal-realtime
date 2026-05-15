from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp

from home import Home
from martingale import Martingale
from trade import Trade


class MainApp(App):

    def build(self):

        self.sm = ScreenManager()

        # ======================
        # SCREENS
        # ======================
        self.sm.add_widget(Home(name="home"))
        self.sm.add_widget(Martingale(name="mart"))
        self.sm.add_widget(Trade(name="trade"))

        self.sm.current = "home"

        # ======================
        # ROOT
        # ======================
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.sm)

        # ======================
        # NAV BAR (UPGRADE)
        # ======================
        nav = BoxLayout(
            size_hint_y=None,
            height=dp(80),
            spacing=dp(10),
            padding=dp(10)
        )

        def make_btn(text, color):
            return Button(
                text=text,
                font_size=dp(16),
                bold=True,
                background_normal="",
                background_color=color,
                color=(0, 0, 0, 1)
            )

        btn_home = make_btn("HOME", (0, 0.9, 1, 1))
        btn_mart = make_btn("MART", (0, 0.7, 1, 1))
        btn_trade = make_btn("TRADE", (0, 0.5, 1, 1))

        btn_home.bind(on_press=lambda x: self.switch("home"))
        btn_mart.bind(on_press=lambda x: self.switch("mart"))
        btn_trade.bind(on_press=lambda x: self.switch("trade"))

        nav.add_widget(btn_home)
        nav.add_widget(btn_mart)
        nav.add_widget(btn_trade)

        root.add_widget(nav)

        return root

    # ======================
    # SWITCH SCREEN
    # ======================
    def switch(self, screen):
        self.sm.current = screen


if __name__ == "__main__":
    MainApp().run()
