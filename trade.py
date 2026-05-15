from kivy.uix.screenmanager import Screen
from jnius import autoclass

Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

class Trade(Screen):

    def on_enter(self):
        intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://stockity.com"))
        currentActivity = PythonActivity.mActivity
        currentActivity.startActivity(intent)
