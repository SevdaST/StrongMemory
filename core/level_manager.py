class LevelManager:
    def __init__(self):
        """
        Manages the level progression of the game.
        """

        # Board sizes for each level
        self.levels = [
            (2, 4),
            (3, 4),
            (4, 4)
        ]

        self.current_level_index = 0

    def get_current_level(self):
        """Returns the current level grid size."""
        return self.levels[self.current_level_index]

    def advance_level(self):
        """Move to the next level if possible."""
        if self.current_level_index < len(self.levels) - 1:
            self.current_level_index += 1
            return True
        return False

    def reset(self):
        """Reset back to level 1."""
        self.current_level_index = 0