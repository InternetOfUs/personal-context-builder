import kivy
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from functools import partial

Builder.load_file("regions.kv")
# Declare both screens


class StartScreen(Screen):
    pass


class UserSelectScreen(Screen):
    pass


# Create the screen manager
sm = ScreenManager()
sm.add_widget(StartScreen(name="start"))
sm.add_widget(UserSelectScreen(name="user_select"))


class TestApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    TestApp().run()
