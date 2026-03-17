import pygame


class CountdownTimer:
    def __init__(self, total_seconds: int):
        """
        Creates a countdown timer.
        total_seconds -> starting time in seconds

        oyun süresini başlatmak
        geri saymak
        bitince game over tetiklemek
        ekranda süreyi göstermek
        """
        # Store the starting time
        self.total_seconds = total_seconds

        # Current remaining time
        self.time_left = total_seconds

        # Indicates whether the timer is currently running
        self.is_running = False

    def start(self) -> None:
        #Starts the timer
        self.is_running = True

    def stop(self) -> None:
        #Stops the timer
        self.is_running = False

    def reset(self) -> None:
        #Resets the timer back to the original starting time and stops it. "
        self.time_left = self.total_seconds
        self.is_running = False

    def update(self, dt: float) -> None:
        #Updates the timer.dt -> delta time in seconds
        # Only decrease time while the timer is running
        if not self.is_running:
            return

        # Reduce remaining time
        self.time_left -= dt

        # Prevent negative time values
        if self.time_left < 0:
            self.time_left = 0

    def is_finished(self) -> bool:
        """Returns True if the timer has reached zero."""
        return self.time_left <= 0

    def get_display_text(self) -> str:
        """ Returns the timer text in a user-friendly format.
            Example: Time: 37
        """
        # Convert float to integer for cleaner display
        return f"Time: {int(self.time_left)}" # f ile krana {} içindeki değeri yazdırılır

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, position: tuple[int, int]) -> None:
        """Draws the timer text on the screen.
           position -> (x, y) position of the text """

        timer_text = font.render(self.get_display_text(), True, (255, 255, 255))
        screen.blit(timer_text, position)