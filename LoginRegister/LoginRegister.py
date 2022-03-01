"""This file contains the login and register functionality."""

# IMPORTS
import re
from datetime import datetime
import requests
import socket
import sys

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, FadeTransition
from kivymd.uix.dialog import MDDialog


class Register(Screen):
    """
    This class handles registration.
    Attributes
    ----------
    email: ObjectProperty
                  The email entered by the user inside the TextField.
    username: ObjectProperty
                  The username entered by the user inside the TextField.
    password: ObjectProperty
                  The password entered by the user inside the TextField.
    confirm_password: ObjectProperty
                  The password confirmation entered by the user inside the TextField.
    errors: List
                  A list to store the errors created when attempting to register with invalid
                  information.
    email_warning: ObjectProperty
                Warning message to tell the user what is wrong with email they entered
    username_warning: ObjectProperty
                Warning message to tell the user what is wrong with username they entered
    password_warning: ObjectProperty
                Warning message to tell the user what is wrong with password they entered
    confirm_password_warning: ObjectProperty
                Warning message to tell the user that the passwords do not match
    """
    email = ObjectProperty(None)
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    confirm_password = ObjectProperty(None)
    email_warning = ObjectProperty(None)
    username_warning = ObjectProperty(None)
    password_warning = ObjectProperty(None)
    confirm_password_warning = ObjectProperty(None)

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)

        self.errors = [False,False,False,False]
        self.warnings = [self.email_warning,self.username_warning,self.password_warning,self.confirm_password_warning]
    def validate(self):
        """
        This function is the registration form's input validation.
        :return validated: A boolean value that is true if all validation checks have been
                           completed successfully.
        """
        # Refresh any previous errors
        self.refresh_errors()

        # Get all users and emails to check if either already exists
        users = requests.get("https://no2project.herokuapp.com/backend_api/no2_backend/users").json()
        emails = []
        usernames = []

        for user in users:
            emails.append(user['email'])
            usernames.append(user['username'])

        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        # If email exists
        if self.email.text in emails:
            self.email_warning.text = "This email is already registered"
            self.errors[0] = True
            self.email.text = ""
            
        # If email is not of email format

        elif not re.fullmatch(email_regex, self.email.text):
            self.email_warning.text = "Please enter a valid email address"
            self.errors[0] = True
            self.email.text = ""

        # If username exists
        if self.username.text in usernames:
            self.username_warning.text = "This username is taken"
            self.errors[1] = True
            self.username.text = ""

        if any(not c.isalnum() for c in self.username.text):
            self.username_warning.text = "Username may only contain alphanumeric characters"
            self.errors[1] = True
            self.username.text = ""
            
        # If a username was not entered
        elif not self.username.text:
            self.username_warning.text = "Please enter a valid username"
            self.errors[1] = True
            self.username.text = ""

        password_regex = re.compile('[!"£$%^&*()_\\-=+/\\\,.><`#~¬]')

        # If password is not between 8 and 15 characters long
        if not 7 < len(self.password.text) < 16:
            self.password_warning.text = "Password must be between 8 and 15 characters long"
            self.errors[2] = True
            self.password.text = ""
            self.confirm_password.text = ""
        # If password does not contain at least one special character
        elif password_regex.search(self.password.text) is None:
            self.password_warning.text = "Password must contain at least one special character"
            self.errors[2] = True
            self.password.text = ""
            self.confirm_password.text = ""

        if self.password.text != self.confirm_password.text or not self.password.text or not self.confirm_password.text:
            self.confirm_password_warning.text = "Passwords must match"
            self.errors[3] = True
            self.password.text = ""
            self.confirm_password.text = ""

        # Check if the user is validated
        validated = True
        for error in self.errors:
            if error:
                validated = False

        return validated

    def refresh_errors(self):
        """This function removes previous error messages when pressing the register button."""
        for i in range(4):
            if self.errors[i]:
                self.errors[i] = False
        self.email_warning.text = ""
        self.username_warning.text = ""
        self.password_warning.text = ""
        self.confirm_password_warning.text = ""

    def register(self):
        """This function creates a new user if validate() returns true."""
        if self.validate():
            # Create new user row
            new_user = {
                "username": self.username.text.strip(),
                "role": "user",
                "email": self.email.text.strip(),
                "password": self.password.text.strip(),
                "registered_on": datetime.now(),
                "last_logged_in": datetime.now(),
                "logged_in": True,
                "allow_emails": True
            }
            # Create new score row for the new user
            new_score = {
                "score_username": self.username.text.strip(),
                "high_score": 0,
                "date_achieved": datetime(2000, 1, 1),
                "previous_score": 0,
                "most_days_lasted": 0,
                "previous_days_lasted": 0
            }
            requests.post('https://no2project.herokuapp.com/backend_api/no2_backend/create/user', data=new_user)
            requests.post('https://no2project.herokuapp.com/backend_api/no2_backend/create/score', data=new_score)

            score = requests.get(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.username.text.strip()}/score').json()

            # Place the user's information in the account screen
            self.manager.account_screen.username = score["score_username"]
            self.manager.account_screen.high_score = score["high_score"]
            self.manager.account_screen.most_days = score["most_days_lasted"]
            self.manager.account_screen.previous_score = score["previous_score"]
            self.manager.account_screen.previous_days = score["previous_days_lasted"]
            self.manager.account_screen.emails = True

            # Log user registration
            hostname = socket.gethostname()
            new_log = {
                "username": score["score_username"],
                "time_occurred": datetime.now(),
                "warning_desc": "user registration and login",
                "ip": socket.gethostbyname(hostname)
            }

            requests.post('https://no2project.herokuapp.com/backend_api/no2_backend/create/log', data=new_log)

            # Clear the registration screen
            self.email.text = ""
            self.username.text = ""
            self.password.text = ""
            self.confirm_password.text = ""

            # Go to account screen
            self.manager.transition = FadeTransition(duration=0.5)
            self.manager.current = "Account"

class Login(Screen):
    """
    This class handles logins.
    Attributes
    ----------
    username: ObjectProperty
                  The username entered by the user inside the TextField.
    password: ObjectProperty
                  The password entered by the user inside the TextField.
    timeout_counter: Integer
                  A counter that causes a timeout if the user fails login thrice in a row.
    """
    username = ObjectProperty(None)
    password = ObjectProperty(None)

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.timeout_counter = 1

    def login(self):
        """
        This function checks the user's credentials and logs them in if they find a match in the
        database.
        Regular users are sent to the account page, the admin is sent to the admin page afterwards.
        If they fail to provide correct credentials 3 times, they are timed out for 60 seconds.
        """
        # Data to validate
        auth_data = {
            "username": self.username.text.strip(),
            "password": self.password.text.strip()
        }

        # Check if user exists and their role
        auth = requests.post('https://no2project.herokuapp.com/backend_api/no2_backend/auth/user', data=auth_data).json()

        # If user exists
        if auth == "Admin" or auth is True:
            # Reset login attempts
            self.timeout_counter = 1

            # Update user's logged_in status to True
            current_user = requests.get(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.username.text.strip()}/user').json()

            updated_user = {
                "username": current_user["username"],
                "role": current_user["role"],
                "email": current_user["email"],
                "password": current_user["password"],
                "registered_on": current_user["registered_on"],
                "last_logged_in": current_user["last_logged_in"],
                "logged_in": True,
                "allow_emails": current_user["allow_emails"]
            }

            requests.put(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.username.text.strip()}/update/user', data=updated_user).json()

            # If user is a regular user
            if auth is True:
                # Place information in account screen
                score = requests.get(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.username.text.strip()}/score').json()

                self.manager.account_screen.username = score["score_username"]
                self.manager.account_screen.high_score = score["high_score"]
                self.manager.account_screen.most_days = score["most_days_lasted"]
                self.manager.account_screen.previous_score = score["previous_score"]
                self.manager.account_screen.previous_days = score["previous_days_lasted"]
                self.manager.account_screen.emails = current_user["allow_emails"]

                # Go to account screen
                self.manager.transition = FadeTransition(duration=0.5)
                self.manager.current = "Account"

                # Log login
                hostname = socket.gethostname()
                new_log = {
                    "username": score["score_username"],
                    "time_occurred": datetime.now(),
                    "warning_desc": "user login",
                    "ip": socket.gethostbyname(hostname)
                }

                requests.post('https://no2project.herokuapp.com/backend_api/no2_backend/create/log', data=new_log)

            # If user is an admin
            elif auth == "Admin":
                # Place admin's username in account screen
                admin = requests.get(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.username.text.strip()}/user').json()

                self.manager.account_screen.username = admin["username"]

                # Go to admin screen
                self.manager.transition = FadeTransition(duration=0.5)
                self.manager.current = "Admin"

                # Log login
                hostname = socket.gethostname()
                new_log = {
                    "username": admin["username"],
                    "time_occurred": datetime.now(),
                    "warning_desc": "admin login",
                    "ip": socket.gethostbyname(hostname)
                }

                requests.post('https://no2project.herokuapp.com/backend_api/no2_backend/create/log', data=new_log)

            # Clear password field
            self.password.text = ""

        # If user doesn't exist
        elif not auth:
            # Clear password field
            self.password.text = ""

            # If user has tries left
            if self.timeout_counter < 3:
                self.timeout_counter += 1
                auth_failed = Popup(title="",
                                    size_hint=(0.4, 0.25))

                box = BoxLayout(orientation='vertical')
                box.add_widget(Label(text="Please check your credentials and try again"))
                box.add_widget(Button(text="Close",
                                      size_hint_y=0.4,
                                      on_release=auth_failed.dismiss))

                auth_failed.add_widget(box)
                auth_failed.open()
            # If user fails to log in within 3 tries
            else:
                # Log unsuccessful login attempt
                hostname = socket.gethostname()
                new_log = {
                    "username": self.password.text.strip(),
                    "time_occurred": datetime.now(),
                    "warning_desc": "unsuccessful login attempt",
                    "ip": socket.gethostbyname(hostname)
                }

                requests.post('https://no2project.herokuapp.com/backend_api/no2_backend/create/log', data=new_log)

                # Reset timeout counter
                self.timeout_counter = 1

                dialog = MDDialog(
                    title="You have had three incorrect login attempts.",
                    text="You are now timed out for 60 seconds",
                    type="alert",
                    auto_dismiss=False

                )
                # Block user
                dialog.open()

                # Unblock user in 60 seconds
                Clock.schedule_once(dialog.dismiss, 60)

    @staticmethod
    def exit_app():
        """This function exits the program."""
        sys.exit(0)
