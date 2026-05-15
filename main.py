from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

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
        # ROOT LAYOUT
        # ======================
        root = BoxLayout(orientation="vertical")

        root.add_widget(self.sm)

        # ======================
        # BOTTOM NAV BAR
        # ======================
        nav = BoxLayout(size_hint_y=None, height=60)

        btn_home = Button(text="HOME")
        btn_mart = Button(text="MART")
        btn_trade = Button(text="TRADE")

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
