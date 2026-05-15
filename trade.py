from kivy_garden.webview import WebView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

import kivy

def open_trade_webview():
    layout = BoxLayout()

    web = WebView(url="https://stockity.com")
    layout.add_widget(web)

    popup = Popup(
        title="TRADE",
        content=layout,
        size_hint=(1, 1)
    )
    popup.open()
