# Import Enum base class from Python standard library
from enum import Enum


class GameState(Enum):
    """
    Represents the current state of the game.

    Each member defines a distinct phase of gameplay.

    Enum, Python’daki enumeration yapisidir.    Sabit ve anlamli isimler tanimlamak için kullanilir

    """

    # Main menu screen
    MENU = 1

    # Active gameplay
    PLAYING = 2

    # Level finished successfully
    LEVEL_COMPLETE = 3

    # Player lost (time over etc.)
    GAME_OVER = 4

    WON = 5

    LOST = 6

    PAUSED = 7