"""This file contains the game's tests."""
from Game.MainGame import Resources, Background, Oxygen, CO2, Score, Temperature, Day, OakTree


Resources.reset_resources()


class TestResources:
    """This class contains tests for the functions of the Resources class."""
    @staticmethod
    def test_reset_resources():
        """
        This function checks if the reset_resources function resets the class variables to
        their original values.
        """
        Resources.oxygen_value = 56
        Resources.oxygen_cap = 150

        Resources.co2_value = 40
        Resources.co2_cap = 236

        Resources.temperature = 50.0
        Resources.days = 40
        Resources.score = 8

        final_oxygen_value = 0
        final_oxygen_cap = 100

        final_co2_value = 0
        final_co2_cap = 100

        final_temperature = 25.0
        final_days = 1
        final_score = 0

        Resources.reset_resources()

        assert Resources.oxygen_value == final_oxygen_value
        assert Resources.oxygen_cap == final_oxygen_cap

        assert Resources.co2_value == final_co2_value
        assert Resources.co2_cap == final_co2_cap

        assert Resources.temperature == final_temperature
        assert Resources.days == final_days
        assert Resources.score == final_score


class TestBackground:
    """This class contains tests for the functions of the Background class."""
    @staticmethod
    def test_update_background():
        """
        This function tests if the update_background function successfully assigns
        the value of co2.co2_percentage into colour_percentage.
        """
        co2 = CO2()
        background = Background(co2)

        background.colour_percentage = 0.3
        background.co2.co2_percentage = 0.6

        background.update_background()

        assert background.colour_percentage == 0.6

        Resources.reset_resources()


class TestOxygen:
    """This class contains tests for the functions of the Oxygen class."""
    @staticmethod
    def test_add_oxygen():
        """
        This function tests if the add_oxygen function adds the intended number into oxygen_value.
        """
        co2 = CO2()
        score = Score()
        oxygen = Oxygen(co2, score)

        oxygen.add_oxygen(73)

        assert oxygen.oxygen_value == 73

        Resources.reset_resources()

    @staticmethod
    def test_add_oxygen_cap():
        """
        This function checks if the add_oxygen_cap() function adds the intended number into oxygen_cap.
        """
        co2 = CO2()
        score = Score()
        oxygen = Oxygen(co2, score)

        oxygen.add_oxygen_cap(65)

        assert oxygen.oxygen_cap == 165

        Resources.reset_resources()

    @staticmethod
    def test_oxygen_click():
        """
        This function checks if the oxygen_click() functions works as intended, resetting
        oxygen_value to 0, reducing co2_value by half of the spent oxygen and adds score equal to
        the oxygen spent.
        """
        co2 = CO2()
        score = Score()
        oxygen = Oxygen(co2, score)

        oxygen.oxygen_value = 60
        Resources.oxygen_value = 60

        co2.co2_value = 50
        Resources.co2_value = 50

        oxygen.oxygen_click()

        assert oxygen.oxygen_value == 0
        assert co2.co2_value == 20
        assert score.score == 30

        Resources.reset_resources()

    @staticmethod
    def test_update_oxygen():
        """
        This function checks if the update_oxygen function correctly updates the values in
        oxygen_value, oxygen_cap with the ones in Resources.oxygen_value and Resources.oxygen_cap.
        """
        oxygen = Oxygen(CO2(), Score())

        Resources.oxygen_value = 50
        Resources.oxygen_cap = 70

        oxygen.update_oxygen()

        assert oxygen.oxygen_value == 50
        assert oxygen.oxygen_cap == 70
        assert oxygen.oxygen_percentage == 50 / 70

        Resources.reset_resources()


class TestCO2:
    """This class contains tests for the functions of the CO2 class."""
    @staticmethod
    def test_add_co2():
        """This function checks if the add_co2() function adds the correct amount to co2_value."""
        co2 = CO2()

        co2.add_co2()

        assert co2.co2_value == 0
        assert round(co2.co2_percentage, 2) == 0

        for i in range(40):
            co2.add_co2()

        assert co2.co2_value == 1
        assert round(co2.co2_percentage, 2) == 0.01

        Resources.reset_resources()

    @staticmethod
    def test_add_co2_cap():
        """
        This function checks if the add_co2_cap() function adds the intended number into co2_cap.
        """
        co2 = CO2()

        co2.co2_value = 12
        Resources.co2_value = 12

        co2.add_co2_cap(20)

        assert co2.co2_cap == 120
        assert co2.co2_percentage == 0.1

        Resources.reset_resources()

    @staticmethod
    def test_update_co2():
        """
        This function checks if the update_co2() function correctly updates the values in
        co2_value, co2_cap with the ones in Resources.co2_value and Resources.co2_cap.
        """
        co2 = CO2()

        Resources.co2_value = 25
        Resources.co2_cap = 50

        co2.update_co2()

        assert co2.co2_value == 25
        assert co2.co2_cap == 50
        assert co2.co2_percentage == 0.5

        Resources.reset_resources()


class TestTemperature:
    """This class contains tests for the functions of the Temperature class."""
    @staticmethod
    def test_add_temp():
        """
        This function checks if the add_temp() function adds the correct amount to temperature.
        """
        temperature = Temperature()

        temperature.add_temp()

        assert temperature.temperature == 24.5 or temperature.temperature == 24.4 or temperature.temperature == 24.6

        Resources.reset_resources()


class TestDay:
    """This class contains tests for the functions of the Day class."""
    @staticmethod
    def test_increment_day():
        """
        This function checks if the increment_day() function adds the correct amount to
        days and Score.score.
        """
        day = Day(Score())

        day.increment_day()

        assert day.days == 2
        assert day.score.score == 2

        Resources.reset_resources()


class TestScore:
    """This class contains tests for the functions of the Score class."""
    @staticmethod
    def test_add_score():
        """This function tests if the add_score() function adds the correct amount to score."""
        score = Score()

        score.add_score(6)

        assert score.score == 6

        Resources.reset_resources()


class TestOakTree:
    """This class contains tests for the functions of the OakTree class."""
    @staticmethod
    def test_ready():
        """This function checks if the ready() function correctly switches is_ready to True."""
        tree = OakTree(0, Oxygen(CO2(), Score()))

        tree.ready()

        assert tree.is_ready

        Resources.reset_resources()

    @staticmethod
    def test_collect_oxygen():
        """
        This function checks if the collect_oxygen() function gives the correct amount of
        oxygen.oxygen_value, increments production, switches is_ready to False and updates
        oxygen.oxygen_percentage.
        """
        tree = OakTree(0, Oxygen(CO2(), Score()))

        tree.collect_oxygen()

        assert tree.oxygen.oxygen_value == 5
        assert tree.production == 6
        assert not tree.is_ready
        assert tree.oxygen.oxygen_percentage == 0.05

        Resources.reset_resources()


Resources.reset_resources()
