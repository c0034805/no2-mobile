"""The game's scoreboard. Here is ranked every player based on their high score."""

# IMPORTS
import requests

from kivy.uix.screenmanager import Screen


class Data(Screen):
    """A class used to create the table layout."""
    pass


class RV(Screen):
    """This class uses RecycleView to load data into the table."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Get the scores table
        scores = requests.get("https://no2project.herokuapp.com/backend_api/no2_backend/scores").json()

        # Leave only usernames, high scores and dates from users who have played before
        self.usernames = []
        self.scores = []
        self.dates = []
        for score in scores:
            if score["high_score"] != 0:
                self.usernames.append(score["score_username"])
                self.scores.append(score['high_score'])
                self.dates.append(score['date_achieved'])

        # Place table data into dictionary
        self.rows = [
            {'Position': str(i + 1),
             'Username': str(self.usernames[i]),
             'Score': str(self.scores[i]),
             'Date': str(self.dates[i])[0:10]
             }
            for i in range(len(self.scores))
        ]

        # Place table data into RecycleView data
        self.rv.data = [{'position': str(x['Position']),
                         'username': str(x['Username']),
                         'score': str(x['Score']),
                         'date': str(x['Date'])} for x in self.rows]

    def partition(self, db_usernames, db_scores, db_dates, left_pointer, right_pointer):
        """
        The partition mechanism of quicksort.

        :param db_usernames: the list of usernames
        :param db_scores: the list of scores
        :param db_dates: the list of dates
        :param left_pointer: left pointer
        :param right_pointer: right pointer

        :return i+1: partition index
        """
        i = left_pointer - 1
        # Sorting based on score so pivot is taken from the score list
        pivot = self.scores[right_pointer]

        for j in range(left_pointer, right_pointer):
            # If a value greater than the pivot is found
            if self.scores[j] > pivot:
                i = i + 1
                # Swap
                db_usernames[i], db_usernames[j] = db_usernames[j], db_usernames[i]
                db_scores[i], db_scores[j] = db_scores[j], db_scores[i]
                db_dates[i], db_dates[j] = db_dates[j], db_dates[i]

        # Swap pivot and associated values
        db_usernames[i + 1], db_usernames[right_pointer] = db_usernames[right_pointer], db_usernames[i + 1]
        db_scores[i + 1], db_scores[right_pointer] = db_scores[right_pointer], db_scores[i + 1]
        db_dates[i + 1], db_dates[right_pointer] = db_dates[right_pointer], db_dates[i + 1]
        return i + 1

    def quick_sort(self, db_usernames, db_scores, db_dates, left_pointer, right_pointer):
        """
        A sorting algorithm which sorts all lists in descending order of scores.

        :param db_usernames: the list of usernames
        :param db_scores: the list of scores
        :param db_dates: the list of dates
        :param left_pointer: left pointer
        :param right_pointer: right pointer
        """
        if len(self.scores) > 1:
            # If pointers have not yet crossed
            if left_pointer < right_pointer:
                partition_index = self.partition(db_usernames,
                                                 db_scores,
                                                 db_dates,
                                                 left_pointer,
                                                 right_pointer)
                self.quick_sort(db_usernames, db_scores, db_dates,
                                left_pointer, partition_index - 1)
                self.quick_sort(db_usernames, db_scores, db_dates,
                                partition_index + 1, right_pointer)


class Scoreboard(Screen):
    """This class builds the scoreboard on screen."""
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.rv = RV()
        self.add_widget(self.rv)

    def refresh_scoreboard(self):
        """This function refreshes the scoreboard."""
        self.remove_widget(self.rv)
        self.rv = RV()
        self.add_widget(self.rv)
