"""The main game."""

# IMPORTS
import random
from datetime import datetime
from functools import partial
import requests

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen


# LAYOUT CLASSES
class Resources:
    """This class stores information accessed by all the other resource classes."""
    # Oxygen variables
    oxygen_value = 0
    oxygen_cap = 100

    # CO2 variables
    co2_value = 0
    co2_cap = 100

    # Label variables
    temperature = 25.0
    days = 1
    score = 0

    @staticmethod
    def reset_resources():
        Resources.oxygen_value = 0
        Resources.oxygen_cap = 100

        Resources.co2_value = 0
        Resources.co2_cap = 100

        Resources.temperature = 25.0
        Resources.days = 1
        Resources.score = 0


class Background(Screen):
    """This class is used for the window's background."""
    def __init__(self, co2, **kwargs):
        Screen.__init__(self, **kwargs)
        self.co2 = co2
        self.colour_percentage = self.co2.co2_percentage

        self.sky_change = Clock.schedule_interval(self.update_background,  0.03)

    def update_background(self, *args):
        """This function updates the background colour percentage."""
        self.colour_percentage = self.co2.co2_percentage


class Oxygen(Screen):
    """
    This class manipulates the oxygen bar.

    Attributes
    ----------
    oxygen_percentage: Float
                       How much of the bar is filled up (value/cap).
    oxygen_value: Integer
                       The current oxygen value.
    oxygen_cap: Integer
                       Maximum possible oxygen value.
    co2: CO2
                       The instance of the CO2 class used when building the final layout.
                       Needed to access and manipulate the current co2 value.
    """
    def __init__(self, co2, score, **kwargs):
        Screen.__init__(self, **kwargs)
        self.oxygen_value = Resources.oxygen_value
        self.oxygen_cap = Resources.oxygen_cap
        self.oxygen_percentage = self.oxygen_value / self.oxygen_cap
        self.co2 = co2
        self.score = score

        # For testing purposes
        # Clock.schedule_interval(self.add_oxygen, 3)

    def add_oxygen(self, value):
        """
        This function changes the current oxygen value and updates the percentage.

        :param value: value to change the oxygen value by
        """
        if Resources.oxygen_value < Resources.oxygen_cap - value:
            Resources.oxygen_value += value
        else:
            Resources.oxygen_value = Resources.oxygen_cap

        self.oxygen_value = round(Resources.oxygen_value)
        self.oxygen_percentage = Resources.oxygen_value / Resources.oxygen_cap

    def add_oxygen_cap(self, value):
        """
        This function changes the maximum oxygen value and updates the percentage.

        :param value: value to change the maximum oxygen value by
        """
        Resources.oxygen_cap += value

        self.oxygen_cap = Resources.oxygen_cap
        self.oxygen_percentage = Resources.oxygen_value / Resources.oxygen_cap

    def oxygen_click(self):
        """
        This function is called when the oxygen bar is clicked. The oxygen bar is reset to 0, the
        CO2 bar is reduced and both bars are then updated.
        """
        if Resources.co2_value - Resources.oxygen_value / 2 > 0:
            Resources.co2_value = Resources.co2_value - Resources.oxygen_value / 2
        else:
            Resources.co2_value = 0

        self.score.add_score(round(Resources.oxygen_value/2))
        Resources.oxygen_value = 0
        self.update_oxygen()
        CO2.update_co2(self.co2)

    def update_oxygen(self):
        """This function updates the oxygen bar."""
        self.oxygen_value = Resources.oxygen_value
        self.oxygen_cap = Resources.oxygen_cap
        self.oxygen_percentage = self.oxygen_value / self.oxygen_cap


class CO2(Screen):
    """
    This class manipulates the CO2 bar.

    Attributes
    ----------
    co2_percentage: Float
                    How much of the bar is filled up (value/cap).
    co2_value: Integer
                    The current co2 value.
    co2_cap: Integer
                    Maximum possible co2 value.
    """
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.co2_value = Resources.co2_value
        self.co2_cap = Resources.co2_cap
        self.co2_percentage = self.co2_value / self.co2_cap

        self.add_co2_event = Clock.schedule_interval(self.add_co2, 0.02487)

    def add_co2(self, *args):
        """This function increases the CO2 value and updates the percentage."""
        if Resources.co2_value + (Resources.days + Resources.temperature) * 0.08 * 0.012435 < 100:
            Resources.co2_value += (Resources.days + Resources.temperature) * 0.08 * 0.012435
        else:
            Resources.co2_value = Resources.co2_cap

        self.co2_value = round(Resources.co2_value)
        self.co2_percentage = Resources.co2_value / Resources.co2_cap

    def add_co2_cap(self, value):
        """
        This function changes the maximum co2 value and updates the percentage.

        :param value: value to change the co2 value by
        """
        Resources.co2_cap += value

        self.co2_cap = Resources.co2_cap
        self.co2_percentage = Resources.co2_value / Resources.co2_cap

    def update_co2(self):
        """This function updates the CO2 bar."""
        self.co2_value = Resources.co2_value
        self.co2_cap = Resources.co2_cap
        self.co2_percentage = self.co2_value / self.co2_cap


class Borders(Screen):
    """This class manipulates the oxygen and CO2 bars' borders."""
    pass


class Icons(Screen):
    """This class manipulates the oxygen and CO2 bars' icons"""
    pass


class Temperature(Screen):
    """
    This class manipulates the temperature display.

    Attributes
    ----------
    temperature: Integer
                 The temperature value.
    """
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.temperature = Resources.temperature

        self.add_temp_event = Clock.schedule_interval(self.add_temp, 2)

    def add_temp(self, *args):
        """This function increases or decreases the temperature value based on the CO2 value."""
        modifier = (Resources.co2_value - 50) / 100

        if modifier > 0:
            modifier *= 2

        choices = [modifier, modifier - 0.1, modifier + 0.1]
        change = random.choices(choices, weights=(50, 25, 25), k=1)[0]

        if 20 < Resources.temperature + change < 60:
            Resources.temperature += change

        self.temperature = round(Resources.temperature, 1)


class Day(Screen):
    """
    This class manipulates the day counter display.

    Attributes
    ----------
    days: Integer
          The day counter.
    """
    def __init__(self, score, **kwargs):
        Screen.__init__(self, **kwargs)
        self.days = Resources.days
        self.score = score

        self.increment_day_event = Clock.schedule_interval(self.increment_day, 2)

    def increment_day(self, *args):
        """This function increments the day counter and adds score."""
        Resources.days += 1
        self.days = Resources.days
        self.score.add_score(2)


class Score(Screen):
    """
    This class manipulates the score display.

    Attributes
    ----------
    score: Integer
           The player's score.
    """
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.score = Resources.score

    def add_score(self, value):
        """This function adds or removes score."""
        Resources.score += value
        self.score = Resources.score


class OakTree:
    """
    This class represents an Oak tree.

    Attributes
    ----------

    i: Integer
       The tree's location on the grid.
    oxygen: Oxygen
       The instance of the oxygen class used when building the final layout.
       Needed to access and manipulate the current co2 value.
    production: Integer
       The amount of oxygen the tree produces.
    is_ready: Boolean
       True if the tree is ready to give oxygen, False if not.
    collect: ClockEvent
       Calls the ready() function at the specified time interval to switch is_ready to True.
    """
    def __init__(self, i, oxygen):
        self.i = i
        self.oxygen = oxygen
        self.production = 5
        self.is_ready = False
        self.collect = Clock.schedule_interval(self.ready, 5)

    def ready(self, *args):
        """This function switches is_ready to True and cancels the ClockEvent which calls it."""
        self.is_ready = True
        self.collect.cancel()

    def collect_oxygen(self):
        """
        This function collects oxygen from the tree.

        is_ready is switched back to False and collect is rescheduled.
        """
        # Collect oxygen in the oxygen bar
        self.oxygen.add_oxygen(self.production)

        # Increase tree production
        if self.production < 10:
            self.production += 1

        # Restart the collection process
        self.is_ready = False
        self.collect()

        # Update oxygen bar
        self.oxygen.update_oxygen()


class GameOverPopup(Popup):
    """
    This class builds the game over popup.

    Attributes
    ----------
    game: Game
          The instance of the game being played.
          Needed to access the window manager to send the player back to the account page.
    """
    def __init__(self, game, **kwargs):
        Popup.__init__(self, **kwargs)
        self.game = game


class TileGrid(Screen):
    """
    This class manipulates the playable grid.

    Attributes
    ----------
    grid: GridLayout
          The main grid where all tiles are placed.
    trees: GridLayout
          A grid of the same size as the above, placed a little higher.
          Its purpose is to place trees in such a way that they go over the
          tile's top border, to go with the slight sideways look of the game.
    production: GridLayout
          A grid to place buttons for the ready-to-collect trees.
    game: Game
          The instance of the game that is being played.
          Needed to access the window manager to send the player back to the account page.
    oxygen: Oxygen
          The instance of the Oxygen class used when building the final layout.
          Needed to access and manipulate the current oxygen value.
    temperature: Temperature
          The instance of the Temperature class used when building the final layout.
          Needed to access the temperature value.
    day: Day
          The instance of the Day class used when building the final layout.
          Needed to access the day counter.
    score: Score
          The instance of the Score class used when building the final layout.
          Needed to access the score adding mechanism.
    flood_used: Boolean
          Switched to true when flood() is called. Used to give the flood() function a cooldown.
    reclaim_used: Boolean
          Switched to true when reclaim() is called. Used to give the reclaim() function a
          cooldown.
    tree_num: Integer
          Number of trees in the grid.
    tree_price: Integer
          (Oxygen) Cost of purchasing a tree.
    confirm_purchase_popup: Popup
          The popup displayed when clicking on an empty grass tile. Gives player the option to
          spend oxygen in exchange for planting a tree on that tile.
    declined: Popup
          The popup displayed when the purchase of a new tree is declined (not enough oxygen).
    game_over_popup: Popup
          The popup displayed when the player loses.
    tree_production: List
          A list of OakTree objects.
          Represents all the trees in the grid.
    tiles: List
          A list of integers. Its size is the grid's rows * columns. Each value in the list
          represents a separate tile state. 0 for grass (empty land to plant trees in), 1 for
          oak_tree (land with oak tree), 2 for water (unusable space) and 3 for locked water
          (water level cannot go below what it is on the starting grid).
    flood_cooldown: ClockEvent
          When at least one tile floods with the flood function, this attribute is used to create
          a minimum cooldown between this and the next time flood can be called again.
    reclaim_cooldown: ClockEvent
          When at least one tile is reclaimed with the reclaim function, this attribute is used to
          create a minimum cooldown between this and the next time reclaim can be called again.
    flood_check: ClockEvent
          Calls the flood function at the specified time interval to flood the grid.
    reclaim_check: ClockEvent
          Calls the reclaim function at the specified time interval to reclaim land previously
          flooded in the grid.
    reload_production_event: ClockEvent
          Calls the reload_production function at the specified time interval to refresh the
          production grid.
    """
    grid = ObjectProperty(None)
    trees = ObjectProperty(None)
    production = ObjectProperty(None)

    def __init__(self, game, oxygen, temperature, day, score, **kwargs):
        Screen.__init__(self, **kwargs)
        self.game = game
        self.oxygen = oxygen
        self.temperature = temperature
        self.day = day
        self.score = score
        self.flood_used = False
        self.reclaim_used = False
        self.tree_num = 1
        self.tree_price = self.tree_num * 3
        self.confirm_purchase_popup = None
        self.declined = None
        self.game_over_popup = None
        self.tree_production = [OakTree(19, self.oxygen)]
        self.tiles = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3,
            0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 3, 3, 3,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3,
            0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3
        ]
        self.flood_cooldown = None
        self.reclaim_cooldown = None
        self.flood_check = Clock.schedule_interval(self.flood, 2)
        self.reclaim_check = Clock.schedule_interval(self.reclaim, 2)
        self.reload_production_event = Clock.schedule_interval(self.reload_production_grid, 1)

    def on_grid(self, *args):
        """
        This function builds the grid layout for the tiles.

        If the tile state specified in self.tiles is equal to 0, a clickable (possible to purchase
        a tree from) grass tile is placed.

        If it is equal to 1 (there is an oak tree there), a non-clickable grass tile is placed.

        If it is equal to 2 or 3(there is water there), a non-clickable water tile is placed.

        :var lost: if all tiles are water then lost is true and game_over() is called.
        """
        lost = True

        for i in range(0, 56):
            if self.tiles[i] == 0:
                self.grid.add_widget(Button(background_normal="Game/Assets/grass.png",
                                            background_down="Game/Assets/grass_pressed.png",
                                            on_press=partial(self.purchase_popup, i)))
                lost = False
            elif self.tiles[i] == 1:
                self.grid.add_widget(Button(background_normal="Game/Assets/grass.png",
                                            background_down="Game/Assets/grass.png"))
                lost = False
            elif self.tiles[i] == 2 or self.tiles[i] == 3:
                self.grid.add_widget(Button(background_normal="Game/Assets/water.png",
                                            background_down="Game/Assets/water.png"))
        if lost:
            self.game_over()

    def on_trees(self, *args):
        """
        This function builds the grid layout for the trees.

        If the tile state specified in self.tiles is equal to 0 or 2, an empty label is placed
        (to keep the grid structure but not interfere with the buttons on the main grid).

        If it is equal to 1, an oak tree is placed.
        """
        for i in range(0, 56):
            if self.tiles[i] == 0 or self.tiles[i] == 2 or self.tiles[i] == 3:
                self.trees.add_widget(Label(text=""))
            elif self.tiles[i] == 1:
                self.trees.add_widget(Button(background_normal="Game/Assets/oak_tree.png",
                                             background_down="Game/Assets/oak_tree.png"))

    def on_production(self, *args):
        """
        This function builds the grid layout for the oxygen collection.

        If the tile state specified in self.tiles is equal to 0 or 2, an empty label is placed
        (to keep the grid structure but not interfere with the buttons on the main grid).

        If it is equal to 1 ie there is an Oak tree there, and it is ready to collect from, a
        button is placed to allow the user to collect oxygen.
        """
        for i in range(0, 56):
            if self.tiles[i] == 0 or self.tiles[i] == 2 or self.tiles[i] == 3:
                self.production.add_widget(Label(text=""))
            elif self.tiles[i] == 1:
                added = False
                for tree in self.tree_production:
                    if tree.i == i and tree.is_ready:
                        self.production.add_widget(Button(background_normal="Game/Assets/oxygen_bubble.png",
                                                          background_down="Game/Assets/oxygen_bubble.png",
                                                          on_release=partial(self.collection_event, tree)))
                        added = True
                if not added:
                    self.production.add_widget(Label(text=""))

    def collection_event(self, tree, *args):
        """
        This function is called when a production button is clicked. It calls the tree's
        collection function, adds score and reloads the production grid.

        :param tree: the tree object to collect from
        """
        tree.collect_oxygen()
        self.score.add_score(1)
        self.reload_production_grid()

    def reload_production_grid(self, *args):
        """This function reloads the production grid."""
        self.production.clear_widgets()
        self.on_production()

    def purchase_popup(self, i, *args):
        """
        This function generates the purchasing decision popup.

        :param i: the tile index

        :var pos: a global variable equal to i so that the purchase_tree() function can access it
        """
        global pos
        pos = i

        self.confirm_purchase_popup = Popup(size_hint_x=0.5,
                                            size_hint_y=0.5,
                                            title="")

        # Build popup layout
        box1 = BoxLayout(orientation="horizontal",
                         size_hint_x=0.3,
                         pos_hint={"center_x": 0.5, "center_y": 0.5})
        box1.add_widget(Image(source="Game/Assets/oxygen_bubble.png",
                              size_hint=(2, 2),
                              pos_hint={"center_x": 0.5, "center_y": 0.5}))
        box1.add_widget(Label(text=str(self.tree_price),
                              font_size=48,
                              bold=True))

        box2 = BoxLayout(orientation="horizontal")
        box2.add_widget(Button(size_hint_y=0.6,
                               text="Yes",
                               on_release=self.purchase_tree))
        box2.add_widget(Button(size_hint_y=0.6,
                               text="No",
                               on_release=self.confirm_purchase_popup.dismiss))

        box = BoxLayout(orientation="vertical")
        box.add_widget(Label(text="Would you like to purchase a tree in this tile?"))
        box.add_widget(box1)
        box.add_widget(box2)

        # Add layout to popup and open
        self.confirm_purchase_popup.add_widget(box)
        self.confirm_purchase_popup.open()

    def purchase_tree(self, *args):
        """
        This function handles the transaction of purchasing a tree.

        :var pos: global variable from purchase_popup() to access tile index
        """
        if Resources.oxygen_value >= self.tree_price:
            # Spend oxygen
            Resources.oxygen_value -= self.tree_price

            # Update tile state
            self.tiles[pos] = 1
            self.tree_production.append(OakTree(pos, self.oxygen))

            # Add oxygen cap
            if Resources.oxygen_cap < 200:
                Resources.oxygen_cap += 5
                self.oxygen.update_oxygen()

            # Update number of trees
            self.tree_num += 1

            # Calculate new tree price
            self.calculate_tree_price()

            # Gain score
            self.score.add_score(5)

            self.confirm_purchase_popup.dismiss()

            # Update oxygen bar and rebuild grid
            self.oxygen.update_oxygen()
            self.grid.clear_widgets()
            self.trees.clear_widgets()
            self.production.clear_widgets()
            self.on_grid()
            self.on_trees()
            self.on_production()
        else:
            self.confirm_purchase_popup.dismiss()

            self.declined = Popup(size_hint_x=0.25,
                                  size_hint_y=0.25,
                                  title="")

            # Build popup layout
            box = BoxLayout(orientation="vertical")
            box.add_widget(Label(text="You do not have enough oxygen!"))
            box.add_widget(Button(text="Close",
                                  size_hint_y=0.27,
                                  on_release=self.declined.dismiss))

            # Add layout to popup and open
            self.declined.add_widget(box)
            self.declined.open()

    def calculate_tree_price(self):
        """This function calculates the price of purchasing a new tree."""
        self.tree_price = self.tree_num * 3

    def flood(self, *args):
        """
        This function changes grass tiles into water tiles when temperature is above 50.

        Each tile adjacent to a water tile has a 15% chance to be flooded.
        """
        if self.temperature.temperature > 50:
            for i in range(0, 56):
                if self.tiles[i] == 2 or self.tiles[i] == 3:
                    adjacent_indexes = self.discover_adjacent_tiles(i)
                    # Iterate through all adjacent tiles
                    for index in adjacent_indexes:
                        # 15% chance
                        if random.randrange(101) < 15:
                            if self.tiles[index] == 1:
                                # Find self.tree_production element to remove
                                tree_production = []
                                for j in range(len(self.tree_production)):
                                    if self.tree_production[j].i != index:
                                        tree_production.append(self.tree_production[j])

                                self.tree_production = tree_production

                            if self.tiles[index] != 2 and self.tiles[index] != 3:
                                self.tiles[index] = 2
                                self.score.add_score(-5)
                                self.flood_used = True

            # Cooldown
            if self.flood_used:
                self.flood_check.cancel()
                self.flood_cooldown = Clock.schedule_once(self.reset_flood, 10)

            self.grid.clear_widgets()
            self.trees.clear_widgets()
            self.production.clear_widgets()
            self.on_grid()
            self.on_trees()
            self.on_production()

    def reset_flood(self, *args):
        """This function reschedules the flood_check ClockEvent."""
        self.flood_used = False
        self.flood_check()

    def reclaim(self, *args):
        """
        This function changes water tiles into grass tiles when temperature is equal or below 32.

        Each tile adjacent to a grass tile has a 20% chance to be reclaimed.
        """
        if self.temperature.temperature < 32.1:
            for i in range(0, 56):
                if self.tiles[i] == 0 or self.tiles[i] == 1:
                    adjacent_indexes = self.discover_adjacent_tiles(i)
                    # Iterate through all adjacent tiles
                    for index in adjacent_indexes:
                        # 20% chance
                        if random.randrange(101) < 20:
                            if self.tiles[index] == 2:
                                self.tiles[index] = 0
                                self.score.add_score(15)
                                self.reclaim_used = True

            # Cooldown
            if self.reclaim_used:
                self.reclaim_check.cancel()
                self.reclaim_cooldown = Clock.schedule_once(self.reset_reclaim, 10)

            self.grid.clear_widgets()
            self.trees.clear_widgets()
            self.production.clear_widgets()
            self.on_grid()
            self.on_trees()
            self.on_production()

    def reset_reclaim(self, *args):
        """This function reschedules the reclaim_check ClockEvent."""
        self.reclaim_used = True
        self.reclaim_check()

    @staticmethod
    def discover_adjacent_tiles(i):
        """This function discovers the adjacent tile indexes of a given tile index."""
        adjacent_indexes = []
        if i == 0:
            adjacent_indexes = [i + 1, i + 15, i + 14]
        elif 0 < i < 13:
            adjacent_indexes = [i + 1, i + 15, i + 14, i + 13, i - 1]
        elif i == 13:
            adjacent_indexes = [i + 14, i + 13, i - 1]
        elif i in (14, 28):
            adjacent_indexes = [i + 1, i + 15, i + 14, i - 14, i - 13]
        elif 14 < i < 27 or 28 < i < 41:
            adjacent_indexes = [i - 1, i - 15, i - 14, i - 13, i + 1, i + 15, i + 14, i + 13]
        elif i in (27, 41):
            adjacent_indexes = [i + 14, i + 13, i - 1, i - 15, i - 14]
        elif i == 42:
            adjacent_indexes = [i + 1, i - 14, i - 13]
        elif 42 < i < 55:
            adjacent_indexes = [i + 1, i - 1, i - 15, i - 14, i - 13]

        return adjacent_indexes

    def game_over(self):
        """This function builds and opens the game over popup."""
        self.game.pause()

        score = requests.get(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.game.manager.account_screen.username}/score').json()

        if Resources.score >= score["high_score"]:
            updated_score = {
                "score_username": score["score_username"],
                "high_score": Resources.score,
                "date_achieved": datetime.now(),
                "previous_score": Resources.score,
                "most_days_lasted": max(Resources.days, score["most_days_lasted"]),
                "previous_days_lasted": Resources.days
            }
        else:
            updated_score = {
                "score_username": score["score_username"],
                "high_score": score["high_score"],
                "date_achieved": score["date_achieved"],
                "previous_score": Resources.score,
                "most_days_lasted": max(Resources.days, score["most_days_lasted"]),
                "previous_days_lasted": Resources.days
            }

        requests.put(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.game.manager.account_screen.username}/update/score', data=updated_score).json()

        score = requests.get(f'https://no2project.herokuapp.com/backend_api/no2_backend/{self.game.manager.account_screen.username}/score').json()
        self.game.manager.account_screen.username = score["score_username"]
        self.game.manager.account_screen.high_score = score["high_score"]
        self.game.manager.account_screen.most_days = score["most_days_lasted"]
        self.game.manager.account_screen.previous_score = score["previous_score"]
        self.game.manager.account_screen.previous_days = score["previous_days_lasted"]

        self.manager.scoreboard.refresh_scoreboard()

        game_over_popup = GameOverPopup(self.game)
        game_over_popup.open()


class PauseButton(Screen):
    """PauseButton class declaration, defined inside pausemenu.kv"""
    def __init__(self, game, **kwargs):
        Screen.__init__(self, **kwargs)
        self.game = game


class Game(Screen):
    """This class adds all widgets to a single Screen."""
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        # Initialise instances of classes in variables so that they can be passed around
        self.co2 = CO2()
        self.background = Background(self.co2)
        self.temperature = Temperature()
        self.score = Score()
        self.oxygen = Oxygen(self.co2, self.score)
        self.day = Day(self.score)
        self.tilegrid = TileGrid(self, self.oxygen, self.temperature, self.day, self.score)

        # Add background
        self.add_widget(self.background)

        # Add oxygen and CO2 bars
        self.add_widget(Borders())
        self.add_widget(Icons())

        # Add mechanisms
        self.add_widget(self.oxygen)
        self.add_widget(self.co2)
        self.add_widget(self.temperature)
        self.add_widget(self.day)
        self.add_widget(self.score)

        # Add the tiles
        self.add_widget(self.tilegrid)

        # Add pause button
        self.add_widget(PauseButton(self))

        # Don't run before user goes to game screen
        self.pause()

    def pause(self):
        """This function pauses the game."""
        self.co2.add_co2_event.cancel()
        self.background.sky_change.cancel()
        self.temperature.add_temp_event.cancel()
        self.day.increment_day_event.cancel()
        self.tilegrid.reload_production_event.cancel()

        if self.tilegrid.flood_used:
            self.tilegrid.flood_cooldown.cancel()
        else:
            self.tilegrid.flood_check.cancel()

        if self.tilegrid.reclaim_used:
            self.tilegrid.reclaim_cooldown.cancel()
        else:
            self.tilegrid.reclaim_check.cancel()

    def resume(self):
        """This function resumes the game."""
        self.co2.add_co2_event()
        self.background.sky_change()
        self.temperature.add_temp_event()
        self.day.increment_day_event()
        self.tilegrid.reload_production_event()

        if self.tilegrid.flood_used:
            self.tilegrid.flood_cooldown()
        else:
            self.tilegrid.flood_check()

        if self.tilegrid.reclaim_used:
            self.tilegrid.reclaim_cooldown()
        else:
            self.tilegrid.reclaim_check()

    def reset_game(self):
        """This function resets the game."""
        Resources.reset_resources()

        self.oxygen.update_oxygen()
        self.co2.update_co2()

        self.temperature.temperature = Resources.temperature
        self.score.score = Resources.score
        self.day.days = Resources.days

        self.tilegrid.oxygen = self.oxygen
        self.tilegrid.temperature = self.temperature
        self.tilegrid.day = self.day
        self.tilegrid.score = self.score

        self.tilegrid.flood_used = False
        self.tilegrid.reclaim_used = False
        self.tilegrid.tree_num = 1
        self.tilegrid.tree_price = self.tilegrid.tree_num * 3
        self.tilegrid.confirm_purchase_popup = None
        self.tilegrid.declined = None
        self.tilegrid.game_over_popup = None
        self.tilegrid.tree_production = [OakTree(19, self.tilegrid.oxygen)]
        self.tilegrid.tiles = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3,
            0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 3, 3, 3,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3,
            0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3
        ]
        self.tilegrid.flood_cooldown = None
        self.tilegrid.reclaim_cooldown = None
        self.tilegrid.flood_check = Clock.schedule_interval(self.tilegrid.flood, 0.03)
        self.tilegrid.reclaim_check = Clock.schedule_interval(self.tilegrid.reclaim, 2)
        self.tilegrid.reload_production_event = Clock.schedule_interval(self.tilegrid.reload_production_grid, 1)

        self.tilegrid.grid.clear_widgets()
        self.tilegrid.trees.clear_widgets()
        self.tilegrid.production.clear_widgets()
        self.tilegrid.on_grid()
        self.tilegrid.on_trees()
        self.tilegrid.on_production()
