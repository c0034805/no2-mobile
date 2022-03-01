"""This file is for handling the account page."""
# IMPORTS
import atexit
from datetime import datetime
import socket
import requests

from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.screenmanager import Screen


class AccountScreen(Screen):
    """This class manipulates the account screen defined in account.kv"""
    username = ObjectProperty(None)
    high_score = ObjectProperty(None)
    most_days = ObjectProperty(None)
    previous_score = ObjectProperty(None)
    previous_days = ObjectProperty(None)
    emails = BooleanProperty()

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        atexit.register(self.sign_out)

    def sign_out(self):
        """This function signs the user out."""
        if self.username is not None or self.username != "":
            current_user = requests.get(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.username}/user').json()

            updated_user = {
                "username": current_user["username"],
                "role": current_user["role"],
                "email": current_user["email"],
                "password": current_user["password"],
                "registered_on": current_user["registered_on"],
                "last_logged_in": datetime.now(),
                "logged_in": False,
                "allow_emails": current_user["allow_emails"]
            }

            requests.put(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.username}/update/user', data=updated_user).json()

            hostname = socket.gethostname()
            if current_user["role"] == "user":
                new_log = {
                    "username": self.username,
                    "time_occurred": datetime.now(),
                    "warning_desc": "user sign out",
                    "ip": socket.gethostbyname(hostname)
                }
            else:
                new_log = {
                    "username": self.username,
                    "time_occurred": datetime.now(),
                    "warning_desc": "admin sign out",
                    "ip": socket.gethostbyname(hostname)
                }

            requests.post('https://no2project.herokuapp.com/backend_api/no2_backend/create/log', data=new_log)

            self.username = ""
            self.high_score = ""
            self.most_days = ""
            self.previous_score = ""
            self.previous_days = ""

            self.manager.game.reset_game()

    def switch_emails(self):
        current_user = requests.get(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.username}/user').json()

        if current_user["allow_emails"]:
            allow = False
        else:
            allow = True

        updated_user = {
            "username": current_user["username"],
            "role": current_user["role"],
            "email": current_user["email"],
            "password": current_user["password"],
            "registered_on": current_user["registered_on"],
            "last_logged_in": current_user["last_logged_in"],
            "logged_in": current_user["logged_in"],
            "allow_emails": allow
        }

        requests.put(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.username}/update/user', data=updated_user).json()

        atexit.register(self.sign_out)
