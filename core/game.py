# Import pygame library for game development functionality
import pygame
# Import project settings (screen size, colors, FPS, etc.)
import settings
from core.game_state import GameState
from entities.board import Board
from ui.timer import CountdownTimer
from core.difficulty import Difficulty
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
        """ Constructor method.
            Runs once when Game object is created.
        """
  
        # Initialize all pygame modules (display, sound, event system, etc.)
        pygame.init()
        # Current difficulty setting
        self.difficulty = Difficulty.EASY
        # Set initial state of the game
        self.is_paused = False
        #self.game_state = "playing"
        #self.state = GameState.MENU   
        self.state = GameState.PLAYING

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
        self.hud_font = pygame.font.SysFont(None, 24)
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

        # Create a countdown timer based on difficulty
        self.timer = CountdownTimer(self.get_time_for_difficulty())
       
        self.level_manager = LevelManager()
        rows, cols = self.level_manager.get_current_level()
        self.board = Board(settings.WIDTH, settings.HEIGHT, rows, cols)

        # Stores the player's current score
        self.score = 0

    def calculate_score(self) -> int:
        """
        Calculates the player's score based on level, remaining time, and moves.
        """

        level_number = self.level_manager.current_level_index + 1
        time_bonus = int(self.timer.time_left * 10)
        move_penalty = self.moves * 5
        level_bonus = level_number * 100

        return level_bonus + time_bonus - move_penalty
    
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

    def get_time_for_difficulty(self) -> int:
        """
        Returns the starting time based on the selected difficulty.
        """
        if self.difficulty == Difficulty.EASY:
            return 60
        elif self.difficulty == Difficulty.MEDIUM:
            return 45
        elif self.difficulty == Difficulty.HARD:
            return 30
        return 60
    
    def handle_events(self):
        """
        Handles all user and system events.

        Responsibilities:
        - Close the window
        - Handle keyboard input
        - Handle mouse input
        - Manage menu, gameplay, restart, and level progression
        """
        #print("events working")
        # Read all events from pygame's event queue
        for event in pygame.event.get():

            # ------------------------------
            # WINDOW CLOSE
            # ------------------------------
            if event.type == pygame.QUIT:

                # Stop the main loop
                self.running = False

            # ------------------------------
            # KEYBOARD INPUT
            # ------------------------------
            elif event.type == pygame.KEYDOWN:

                # --- DEBUG / STATE TEST KEYS ---
                if event.key == pygame.K_1: self.state = GameState.MENU
                elif event.key == pygame.K_2: 
                    self.state = GameState.PLAYING 
                    self.timer.start()

                elif event.key == pygame.K_3:
                    self.state = GameState.LEVEL_COMPLETE

                elif event.key == pygame.K_4:
                    self.state = GameState.GAME_OVER

                # --- START GAME FROM MENU ---
                elif event.key == pygame.K_RETURN:
                    if self.state == GameState.MENU:

                        # Reset timer based on selected difficulty
                        self.timer = CountdownTimer(self.get_time_for_difficulty())
                        self.timer.start()

                        # Start playing
                        self.state = GameState.PLAYING

                # --- DIFFICULTY SELECTION ---
                elif event.key == pygame.K_q:
                    self.difficulty = Difficulty.EASY

                    # Recreate timer with new difficulty time
                    self.timer = CountdownTimer(self.get_time_for_difficulty())

                elif event.key == pygame.K_w:
                    self.difficulty = Difficulty.MEDIUM

                    # Recreate timer with new difficulty time
                    self.timer = CountdownTimer(self.get_time_for_difficulty())

                elif event.key == pygame.K_e:
                    self.difficulty = Difficulty.HARD

                    # Recreate timer with new difficulty time
                    self.timer = CountdownTimer(self.get_time_for_difficulty())

                # --- RESTART CURRENT BOARD ---
                elif event.key == pygame.K_r:
                    self.reset_game()

                # --- GO BACK TO MENU ---
                elif event.key == pygame.K_m:
                    self.state = GameState.MENU
                    self.timer.stop()

                # --- NEXT LEVEL ---
                elif event.key == pygame.K_n:
       
                    if self.state == GameState.LEVEL_COMPLETE:

                        has_next_level = self.level_manager.advance_level()

                        if has_next_level:
                            self.load_current_level()

                        else:
                            self.state = GameState.GAME_OVER
                # --- PAuse ---            
                elif event.key == pygame.K_ESCAPE:

                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED

                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
            # ------------------------------
            # MOUSE INPUT
            # ------------------------------
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Only allow clicks while playing
                
                if self.state != GameState.PLAYING:
                    continue
                # Prevent clicking while waiting
                if self.board_locked:
                    continue

                # Get mouse position
                mouse_pos = event.pos

                # Check clicked card
                for card in self.board.cards:

                    # Ignore if mouse is not inside
                    if not card.contains_point(mouse_pos):
                        continue

                    # Ignore matched cards
                    if card.is_matched:
                        break

                    # Ignore already flipped cards
                    if card.is_flipped:
                        break

                    # Flip card
                    card.flip()

                    # Save first card
                    if self.first_card is None:
                        self.first_card = card

                    # Save second card
                    elif self.second_card is None:

                        self.second_card = card

                        self.moves += 1

                        self.board_locked = True

                        self.flip_back_start_time = pygame.time.get_ticks()

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
        if self.state == GameState.PLAYING or self.state == GameState.PAUSED:

            # Draw all cards on the board
            self.board.draw_cards(self.screen, self.font)

            # Draw move counter in the top-left corner
            moves_text = self.hud_font.render(f"Moves: {self.moves}",True,(255, 255, 255) )
            self.screen.blit(moves_text, (20, 20))
            self.timer.draw(self.screen, self.hud_font, (150, 20))

            level_number = self.level_manager.current_level_index + 1
            level_text = self.hud_font.render(f"Level: {level_number}",True,(255,255,255))
            difficulty_text = self.hud_font.render(f"Difficulty: {self.difficulty.value}", True,(255, 255, 255))
            # Calculate live score during gameplay
            live_score = self.calculate_score()

            score_text = self.hud_font.render(f"Score: {live_score}",True,(255, 255, 255))
            self.screen.blit(score_text, (600, 20))

            self.screen.blit(difficulty_text, (300, 20))
            self.screen.blit(level_text, (500,20))
        # ------------------------------
        # LEVEL COMPLETE STATE
        # ------------------------------
        elif self.state == GameState.LEVEL_COMPLETE:

            # Create a message for level completion
            complete_text = self.font.render("Level Complete!",True,(255, 255, 255))

            # Center the message on the screen
            complete_rect = complete_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))
            self.screen.blit(complete_text, complete_rect)
            next_text = self.font.render("Press N for Next Level",True,(255,255,255))
            next_rect = next_text.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 + 80))
            self.screen.blit(next_text, next_rect)

            score_text = self.font.render(f"Score: {self.score}", True,(255, 255, 255))
            score_rect = score_text.get_rect(center=((settings.WIDTH // 2)-40, (settings.HEIGHT // 2)-80))
            self.screen.blit(score_text, score_rect)

            score_text = self.hud_font.render(f"Score: {self.score}",True,(255, 255, 255))
            self.screen.blit(score_text, (320, 20))
        # ------------------------------
        # GAME OVER STATE
        # ------------------------------
        elif self.state == GameState.GAME_OVER:

            # Create a game over message
            game_over_text = self.font.render("Game Over",True,(255, 255, 255))
            game_exit_text = self.font.render("To exit press 0",True,(255,255,255))
            # Center the message on the screen
            game_over_rect = game_over_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))
            game_exit_rect = game_exit_text.get_rect(center=((settings.WIDTH // 2)+30, (settings.HEIGHT // 2)+60))
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(game_exit_text, game_exit_rect)
            next_text = self.font.render("Press N for Next Level",True,(255,255,255))

        # ------------------------------
        # MENU STATE
        # ------------------------------
      

        elif self.state == GameState.MENU:

            title = self.font.render("Memory Game", True,(255,255,255))
            start_text = self.font.render("Press ENTER to Start", True, (255,255,255))
            difficulty_text = self.font.render(f"Difficulty: {self.difficulty.value}",True,(255,255,255))

            title_rect = title.get_rect(center=(settings.WIDTH//2,200))
            start_rect = start_text.get_rect(center=(settings.WIDTH//2,300))
            diff_rect = difficulty_text.get_rect(center=(settings.WIDTH//2,350))

            self.screen.blit(title,title_rect)
            self.screen.blit(start_text,start_rect)
            self.screen.blit(difficulty_text,diff_rect)

        if self.state == GameState.PAUSED:
            pause_text = self.font.render(
                "PAUSED",
                True,
                (255, 255, 0)
            )

            text_rect = pause_text.get_rect(
                center=(settings.WIDTH // 2, settings.HEIGHT // 2)
            )

            self.screen.blit(pause_text, text_rect)
        
        # Update the full display
        if self.state == GameState.WON:

            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))

            self.screen.blit(overlay, (0, 0))

            text = self.font.render("YOU WIN!", True, (255, 215, 0))

            text_rect = text.get_rect(
                center=(settings.WIDTH // 2, settings.HEIGHT // 2)
            )

            self.screen.blit(text, text_rect)

        if self.state == GameState.LOST:

            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))

            self.screen.blit(overlay, (0, 0))

            text = self.font.render("GAME OVER", True, (255, 80, 80))

            text_rect = text.get_rect(
                center=(settings.WIDTH // 2, settings.HEIGHT // 2)
            )

            self.screen.blit(text, text_rect)

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
        if self.state != GameState.PLAYING:
            return
        mouse_pos = pygame.mouse.get_pos()

        for card in self.board.cards:
            card.is_hovered = card.contains_point(mouse_pos)
              # Only update gameplay while playing
            if self.state != GameState.PLAYING:
                return

        # Update countdown timer
        self.timer.update(dt)
        if all(card.is_matched for card in self.board.cards):
            self.game_state = GameState.WON
        if self.timer.time_left <= 0:
            self.game_state = GameState.LOST
        for card in self.board.cards:
            card.update(dt)
        # Update current score during gameplay
        self.score = self.calculate_score()

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
            self.score = self.calculate_score()
            self.timer.stop()
            self.state = GameState.LEVEL_COMPLETE

    def reset_game(self):
        """
        Resets the current board with the same grid size.
        """

        # Create a new board with the current grid size
        self.board = Board(settings.WIDTH,settings.HEIGHT,self.board.rows,self.board.cols)

        # Reset matching logic
        self.first_card = None
        self.second_card = None
        self.board_locked = False
        self.flip_back_start_time = None

        # Reset move counter
        self.moves = 0

        # Reset timer
        self.timer = CountdownTimer(self.get_time_for_difficulty())
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

        self.timer = CountdownTimer(self.get_time_for_difficulty())
        self.timer.start()

        self.state = GameState.PLAYING

    def calculate_score(self) -> int:
        """
        Calculates the player's score.

        Score formula:
        - level bonus increases with level number
        - remaining time gives bonus points
        - more moves reduce the score
        """

        # Current level number starts from 1
        level_number = self.level_manager.current_level_index + 1

        # Bonus for reaching higher levels
        level_bonus = level_number * 100

        # Bonus for remaining time
        time_bonus = int(self.timer.time_left * 10)

        # Penalty for using too many moves
        move_penalty = self.moves * 5

        # Final score
        return level_bonus + time_bonus - move_penalty
if __name__ == "__main__":
    game = Game()
    game.run()