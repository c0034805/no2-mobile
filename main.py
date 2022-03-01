# IMPORTS
import requests

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog

from NewsPage.NewsPage import NewsScreen
from Game.MainGame import Game
from Game.PauseMenu.PauseMenu import PauseMenu
from Account.Account import AccountScreen
from Account.Scoreboard import Scoreboard
from LoginRegister.LoginRegister import Login, Register
from AdminPage.Admin import AdminScreen, LogsScreen

# WINDOW CONFIGURATION
Window.fullscreen = True


class Manager(ScreenManager):
    """WindowManager inherits ScreenManager class for displaying and transitioning between screens"""
    last_screen = None
    login = ObjectProperty()
    register = ObjectProperty()
    account_screen = ObjectProperty()
    scoreboard = ObjectProperty()
    game = ObjectProperty()
    pause_menu = ObjectProperty()
    news_screen = ObjectProperty()
    admin_screen = ObjectProperty()
    log_screen = ObjectProperty()
    pass


class WindowManagerApp(MDApp):
    """The final application."""
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.title = "nO2"
        self.icon = "Game/Assets/oak_tree.png"

        #try:
        requests.get("https://no2project.herokuapp.com/backend_api/", timeout=10)
        return Manager()
        """except (requests.ConnectionError, requests.Timeout) as exception:
            dialog = MDDialog(
                    title="No connection",
                    text="An unexpected error was encountered when trying to connect to the server.",
                    type="alert",
                    auto_dismiss=False
                )
            dialog.open()"""


if __name__ == "__main__":
    WindowManagerApp().run()
