from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from home import Home
from martingale import Martingale


class MainApp(App):

    def build(self):

        sm = ScreenManager()

        sm.add_widget(Home(name="home"))
        sm.add_widget(Martingale(name="mart"))

        sm.current = "home"

        return sm


if __name__ == "__main__":
    MainApp().run()
