# Import pygame library for game development functionality
import pygame

# Import project settings (screen size, colors, FPS, etc.)
import settings


class Game:
    """
    Main Game class.
    Responsible for:
    - Initializing pygame
    - Creating the window
    - Running the main loop
    - Handling events
    - Drawing everything on screen
    """

    def __init__(self):
        """
        Constructor method.
        Runs once when Game object is created.
        """

        # Initialize all pygame modules (display, sound, event system, etc.)
        pygame.init()

        # Create the main window using width and height from settings
        self.screen = pygame.display.set_mode(
            (settings.WIDTH, settings.HEIGHT)
        )

        # Set the window title
        pygame.display.set_caption("Boost Your Memory")

        # Create a clock object to control frame rate (FPS)
        self.clock = pygame.time.Clock()

        # Control variable for the main game loop
        self.running = True

    def run(self):
        """
        Main game loop.
        Runs continuously until self.running becomes False.
        """

        # Loop runs while the game is active
        while self.running:

            # Limit the loop to defined FPS (prevents excessive CPU usage)
            self.clock.tick(settings.FPS)

            # Handle user input and system events
            self.handle_events()

            # Draw everything on the screen
            self.draw()

        # When loop exits, properly close pygame
        pygame.quit()

    def handle_events(self):
        """
        Handles all user and system events.
        Example:
        - Window close
        - Keyboard input
        - Mouse input
        """

        # Get all events from pygame event queue
        for event in pygame.event.get():

            # If user clicks the window close button
            if event.type == pygame.QUIT:

                # Stop the main loop
                self.running = False

    def draw(self):
        """
        Responsible for rendering graphics on the screen.
        """

        # Fill the screen with background color
        self.screen.fill(settings.BACKGROUND_COLOR)

        # Update the full display surface to the screen
        pygame.display.flip()