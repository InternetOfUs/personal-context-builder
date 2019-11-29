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

    def load_from_csv(self):
        App.get_running_app().user_select_screen.update_user_list(
            ["user from csv 1", "user from csv 2"]
        )


class UserSelectScreen(Screen):
    pass

    def update_user_list(self, user_list):
        self.ids.user_list.text = "\n".join(user_list)


class MapsScreen(Screen):
    pass


Config.set("graphics", "width", "1900")
Config.set("graphics", "height", "1000")

user_select_screen = UserSelectScreen(name="user_select")

sm = ScreenManager()
sm.add_widget(StartScreen(name="start"))
sm.add_widget(user_select_screen)
sm.add_widget(MapsScreen(name="maps"))


class TestApp(App):
    user_select_screen = user_select_screen

    def build(self):
        return sm


if __name__ == "__main__":
    TestApp().run()
