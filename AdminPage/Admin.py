"""The screen that contains all of the admins' functions"""

# IMPORTS
import atexit
import requests

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout


class AdminScreen(Screen):
    """AdminScreen class declaration, defined inside admin.kv"""
    def sign_admin_out(self):
        atexit.register(self.manager.account_screen.sign_out)


class Entry(BoxLayout):
    """Entry class to represent log entries in the RecycleView"""
    pass


class Log(RecycleView):
    """Log class to show the log entries to the  Admin"""
    def __init__(self,**kwargs):
        super(Log, self).__init__(**kwargs)
        # Fills the log when the screen is created
        self.refresh_log()

    def refresh_log(self):
        # Gets log entries from the database
        items = requests.get('https://no2project.herokuapp.com/backend_api/no2_backend/logs').json()
        # Reverses the order so more recent entries are displayed first
        items.reverse()
        self.data = [{'username': x['username'],
                      'time_occurred': x['time_occurred'][0:10] + " " + x["time_occurred"][12:19],
                      'ip_address': x['ip'],
                      'warning_desc': x['warning_desc']} for x in items[:25]]


class LogsScreen(Screen):
    """LogsScreen class declaration, defined inside admin.kv"""
    log = ObjectProperty()
    pass
