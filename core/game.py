# Import pygame library for game development functionality
import pygame

# Import project settings (screen size, colors, FPS, etc.)
import settings

from core.game_state import GameState

from entities.board import Board

from ui.timer import CountdownTimer

from core.level_manager import LevelManager

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

        # Set initial state of the game
        self.state = GameState.MENU

        # Create the main window using width and height from settings
        self.screen = pygame.display.set_mode(
            (settings.WIDTH, settings.HEIGHT)
        )

        # Set the window title
        pygame.display.set_caption("Boost Your Memory")

        # create board (GRID)
        self.board = Board(settings.WIDTH, settings.HEIGHT, rows=2, cols=4)

        # Create a clock object to control frame rate (FPS)
        self.clock = pygame.time.Clock()

        # Control variable for the main game loop
        self.running = True

        self.font = pygame.font.SysFont(None, 48)

        # Stores the first selected card
        self.first_card = None

        # Stores the second selected card
        self.second_card = None

        # Counts how many move attempts the player has made
        # One move = selecting two cards
        self.moves = 0

        # Prevents clicking new cards while waiting
        self.board_locked = False

        # Delay before flipping unmatched cards back (milliseconds)
        self.flip_back_delay = 800

        # Time when the second card was selected
        self.flip_back_start_time = None

        # Create a 60-second countdown timer
        self.timer = CountdownTimer(15)
       
        self.level_manager = LevelManager()
        rows, cols = self.level_manager.get_current_level()
        self.board = Board(settings.WIDTH, settings.HEIGHT, rows, cols)

    def run(self):
        """
        Main game loop.
        Runs continuously until self.running becomes False.
        """

        # Loop runs while the game is active
        while self.running:


            # Limit the loop to defined FPS (prevents excessive CPU usage)
            #self.clock.tick(settings.FPS)
            dt = self.clock.tick(settings.FPS) / 1000

            # Handle user input and system events
            self.handle_events()
            self.update(dt)
            # Draw everything on the screen
            self.draw()

        # When loop exits, properly close pygame
        pygame.quit()

    def handle_events(self):
        """
        Handles all user and system events.

        Examples:
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

            # --- TEST STATE TRANSITIONS ---
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    self.state = GameState.MENU

                elif event.key == pygame.K_2:
                    self.state = GameState.PLAYING
                    self.timer.start()

                elif event.key == pygame.K_3:
                    self.state = GameState.LEVEL_COMPLETE

                elif event.key == pygame.K_4:
                    self.state = GameState.GAME_OVER

                elif event.key == pygame.K_r:
                    self.reset_game()

                elif event.key == pygame.K_n:
                    if self.state == GameState.LEVEL_COMPLETE:
                        has_next = self.level_manager.advance_level()
                        if has_next:
                            self.load_current_level()
                        else:
                            self.state = GameState.GAME_OVER

            # --- WEEK 4: CARD CLICK + MATCHING PREPARATION ---
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # Only allow clicking cards while playing
                if self.state != GameState.PLAYING:
                    continue

                # Do not allow clicks while the board is locked
                if self.board_locked:
                    continue

                # Get mouse position
                mouse_pos = event.pos

                # Check which card was clicked
                for card in self.board.cards:

                    # Check if mouse click is inside this card
                    if card.contains_point(mouse_pos):

                        # Do not allow clicking matched cards
                        if card.is_matched:
                            break

                        # Do not allow clicking an already flipped card
                        if card.is_flipped:
                            break

                        # Flip the clicked card
                        card.flip()

                        # Save as first selected card
                        if self.first_card is None:
                            self.first_card = card

                        # Save as second selected card, count the move, and lock the board
                        elif self.second_card is None:
                            self.second_card = card

                            # One move is completed when the second card is selected
                            self.moves += 1

                            # Lock the board until cards are compared
                            self.board_locked = True
                            self.flip_back_start_time = pygame.time.get_ticks()

                        # Stop after handling one clicked card
                        break
    def draw(self):
        """
        Draw everything on the screen.

        Responsibilities:
        - Clear the screen
        - Draw cards during gameplay
        - Draw move counter
        - Show simple state messages
        """

        # Fill the entire screen with the background color
        self.screen.fill(settings.BACKGROUND_COLOR)

            # ------------------------------
            # PLAYING STATE
            # ------------------------------
        if self.state == GameState.PLAYING:

            # Draw all cards on the board
            self.board.draw_cards(self.screen, self.font)

            # Draw move counter in the top-left corner
            moves_text = self.font.render(
                f"Moves: {self.moves}",
                True,
                (255, 255, 255)
            )
            self.screen.blit(moves_text, (20, 20))
            self.timer.draw(self.screen, self.font, (20, 70))
            level_number = self.level_manager.current_level_index + 1

            level_text = self.font.render(
                f"Level: {level_number}",
                True,
                (255,255,255)
            )

            self.screen.blit(level_text, (20,120))
        # ------------------------------
        # LEVEL COMPLETE STATE
        # ------------------------------
        elif self.state == GameState.LEVEL_COMPLETE:

            # Create a message for level completion
            complete_text = self.font.render(
                "Level Complete!",
                True,
                (255, 255, 255)
            )

            # Center the message on the screen
            complete_rect = complete_text.get_rect(
                center=(settings.WIDTH // 2, settings.HEIGHT // 2)
            )

            self.screen.blit(complete_text, complete_rect)
            next_text = self.font.render("Press N for Next Level",True,(255,255,255))
            next_rect = next_text.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 + 80))
            self.screen.blit(next_text, next_rect)
        # ------------------------------
        # GAME OVER STATE
        # ------------------------------
        elif self.state == GameState.GAME_OVER:

            # Create a game over message
            game_over_text = self.font.render(
                "Game Over",
                True,
                (255, 255, 255)
            )

            # Center the message on the screen
            game_over_rect = game_over_text.get_rect(
                center=(settings.WIDTH // 2, settings.HEIGHT // 2)
            )

            self.screen.blit(game_over_text, game_over_rect)

        # ------------------------------
        # MENU STATE
        # ------------------------------
        elif self.state == GameState.MENU:

            # Simple menu text
            menu_text = self.font.render(
                "Press 2 to Start Playing",
                True,
                (255, 255, 255)
            )

            # Center the menu text
            menu_rect = menu_text.get_rect(
                center=(settings.WIDTH // 2, settings.HEIGHT // 2)
            )

            self.screen.blit(menu_text, menu_rect)

        # Update the full display
        pygame.display.flip()

    def update(self, dt):
        """
        Updates the game logic.

        Responsibilities:
        - Update the timer
        - Compare selected cards
        - Flip back unmatched cards after a delay
        - Detect level completion
        """

        # Only update gameplay while playing
        if self.state != GameState.PLAYING:
            return

        # Update countdown timer
        self.timer.update(dt)

        # If time runs out, game is over
        if self.timer.is_finished():
            self.state = GameState.GAME_OVER
            return

        # ---------------------------------
        # Handle card comparison
        # ---------------------------------
        if self.first_card is not None and self.second_card is not None:

            # If the two selected cards match
            if self.first_card.value == self.second_card.value:

                # Keep both cards permanently open
                self.first_card.is_matched = True
                self.second_card.is_matched = True

                # Clear selection state
                self.first_card = None
                self.second_card = None
                self.board_locked = False
                self.flip_back_start_time = None

            else:
                # Wait before flipping unmatched cards back
                current_time = pygame.time.get_ticks()

                if current_time - self.flip_back_start_time >= self.flip_back_delay:

                    # Flip both cards back
                    self.first_card.flip()
                    self.second_card.flip()

                    # Clear selection state
                    self.first_card = None
                    self.second_card = None
                    self.board_locked = False
                    self.flip_back_start_time = None

        # ---------------------------------
        # Check if all cards are matched
        # ---------------------------------
        all_matched = True

        for card in self.board.cards:
            if not card.is_matched:
                all_matched = False
                break

        if all_matched:
            self.timer.stop()
            self.state = GameState.LEVEL_COMPLETE

    def reset_game(self):
        """
        Resets the current board with the same grid size.
        """

        # Create a new board with the current grid size
        self.board = Board(
            settings.WIDTH,
            settings.HEIGHT,
            self.board.rows,
            self.board.cols
        )

        # Reset matching logic
        self.first_card = None
        self.second_card = None
        self.board_locked = False
        self.flip_back_start_time = None

        # Reset move counter
        self.moves = 0

        # Reset timer
        self.timer.reset()
        self.timer.start()

        # Return to PLAYING state
        self.state = GameState.PLAYING

    def load_current_level(self):
        """
        Loads the board for the current level.
        """

        rows, cols = self.level_manager.get_current_level()

        self.board = Board(settings.WIDTH, settings.HEIGHT, rows, cols)

        self.first_card = None
        self.second_card = None
        self.board_locked = False
        self.flip_back_start_time = None

        self.moves = 0

        self.timer.reset()
        self.timer.start()

        self.state = GameState.PLAYING
if __name__ == "__main__":
    game = Game()
    game.run()