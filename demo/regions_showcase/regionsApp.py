import kivy
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.config import Config
from functools import partial

Builder.load_file("regions.kv")


class StartScreen(Screen):
    pass


class UserSelectScreen(Screen):
    pass


class MapsScreen(Screen):
    pass


Config.set("graphics", "width", "1900")
Config.set("graphics", "height", "1000")

sm = ScreenManager()
sm.add_widget(StartScreen(name="start"))
sm.add_widget(UserSelectScreen(name="user_select"))
sm.add_widget(MapsScreen(name="maps"))


class TestApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    TestApp().run()
