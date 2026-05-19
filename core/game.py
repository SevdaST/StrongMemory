# Import pygame library for game development functionality
import pygame
import random
import settings
import math
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
        self.state = GameState.MENU   
        #self.state = GameState.PLAYING

        # Create the main window using width and height from settings
        #self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        settings.WIDTH, settings.HEIGHT = self.screen.get_size()
        # Set the window title
        pygame.display.set_caption("Boost Your Memory")

        # create board (GRID)
        
        self.level_manager = LevelManager()
        rows, cols = self.level_manager.get_current_level()
        self.board = Board(settings.WIDTH, settings.HEIGHT, rows, cols, self.difficulty)

        # Create a clock object to control frame rate (FPS)
        self.clock = pygame.time.Clock()

        # Control variable for the main game loop
        self.running = True

        self.font = pygame.font.SysFont(None, 40)
        self.hud_font = pygame.font.SysFont(None, 28)
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
        self.board = Board(settings.WIDTH, settings.HEIGHT, self.board.rows,self.board.cols, self.difficulty)

        # Stores the player's current score
        self.score = 0
        self.marquee_x = settings.WIDTH
        self.explosions = []
        self.explosion_timer = 0
        self.emoji_font = pygame.font.SysFont("Segoe UI Emoji", 32)
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

                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                 # --- START GAME FROM MENU ---
                if event.key == pygame.K_RETURN:
                    if self.state == GameState.MENU:

                        self.timer = CountdownTimer(self.get_time_for_difficulty())
                        self.timer.start()

                        self.state = GameState.PLAYING
               
                # --- RESTART CURRENT BOARD ---
                elif event.key == pygame.K_r:
                    self.reset_game()

                elif event.key == pygame.K_q:
                    if self.state in [GameState.MENU, GameState.PAUSED]:
                        self.running = False

                # --- GO BACK TO MENU ---
                elif event.key == pygame.K_m:
                    if self.state in [GameState.PAUSED, GameState.GAME_OVER, GameState.LEVEL_COMPLETE]:
                        self.timer.stop()
                        self.state = GameState.MENU
                        
                # --- NEXT LEVEL ---
                elif event.key == pygame.K_n:

                    if self.state == GameState.LEVEL_COMPLETE:

                        has_next_level = self.level_manager.advance_level()

                        # Same difficulty next level
                        if has_next_level:

                            self.load_current_level()

                        # Difficulty completed
                        else:

                            if self.difficulty == Difficulty.EASY:
                                self.difficulty = Difficulty.MEDIUM

                            elif self.difficulty == Difficulty.MEDIUM:
                                self.difficulty = Difficulty.HARD

                            # Reset levels for new difficulty
                            self.level_manager = LevelManager()

                            self.load_current_level()
                                
            # ------------------------------
            # MOUSE INPUT
            # ------------------------------
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                mouse_pos = event.pos

                # Menu clicks
                if self.state == GameState.MENU:

                    if self.easy_rect and self.easy_rect.collidepoint(mouse_pos):
                        self.difficulty = Difficulty.EASY

                    elif self.medium_rect and self.medium_rect.collidepoint(mouse_pos):
                        self.difficulty = Difficulty.MEDIUM

                    elif self.hard_rect and self.hard_rect.collidepoint(mouse_pos):
                        self.difficulty = Difficulty.HARD

                    elif self.start_rect and self.start_rect.collidepoint(mouse_pos):

                        self.level_manager = LevelManager()
                        rows, cols = self.level_manager.get_current_level()
                        self.board = Board(settings.WIDTH, settings.HEIGHT, rows, cols, self.difficulty)

                        self.first_card = None
                        self.second_card = None
                        self.board_locked = False
                        self.flip_back_start_time = None
                        self.moves = 0

                        self.timer = CountdownTimer(self.get_time_for_difficulty())
                        self.timer.start()

                        self.state = GameState.PLAYING

                    continue
                
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

            # ✅ Draw HUD panel background FIRST, then blit text on top
            self.board.draw_hud_panel(self.screen)

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

            is_last_level = self.level_manager.current_level_index == len(self.level_manager.levels) - 1

            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 0))
            self.screen.blit(score_text, score_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 150)))

            complete_text = self.font.render("Level Complete!", True, (255, 255, 0))
            self.screen.blit(complete_text, complete_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 70)))

            if is_last_level:

                congrats_text = self.font.render("Congratulations!", True, (255, 255, 0))
                self.screen.blit(congrats_text, congrats_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 220)))

                if self.difficulty == Difficulty.EASY:
                    difficulty_message = "Easy difficulty completed! Press N to move to Medium"
                elif self.difficulty == Difficulty.MEDIUM:
                    difficulty_message = "Medium difficulty completed! Press N to move to Hard"
                else:
                    difficulty_message = "Hard difficulty completed! You finished the game!"

                pulse = abs(math.sin(pygame.time.get_ticks() * 0.004))
                glow_color = (255, 255, int(150 + pulse * 105))

                message_text = self.hud_font.render(difficulty_message, True, glow_color)
                self.screen.blit(message_text, message_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 20)))

                for i in range(8):
                    x = 120 + i * 140
                    y = 120 + int(20 * math.sin(pygame.time.get_ticks() * 0.003 + i))
                    pygame.draw.circle(self.screen, (255, 80, 120), (x, y), 18)
                    pygame.draw.line(self.screen, (255, 255, 255), (x, y + 18), (x, y + 55), 2)

            else:

                next_text = self.hud_font.render("Press N for Next Level", True, (255, 255, 0))
                self.screen.blit(next_text, next_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 20)))

            menu_text = self.hud_font.render("Press M for Main Menu", True, (255, 255, 255))
            self.screen.blit(menu_text, menu_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 90)))
        # ------------------------------
        # GAME OVER STATE
        # ------------------------------
        elif self.state == GameState.GAME_OVER:

            game_over_text = self.font.render("Game Over", True, (255, 80, 80))
            self.screen.blit(game_over_text, game_over_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 160)))

            retry_text = self.hud_font.render("Press A to Play Again", True, (255, 255, 0))
            self.screen.blit(retry_text, retry_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 40)))

            menu_text = self.hud_font.render("Press M for Main Menu", True, (255, 255, 255))
            self.screen.blit(menu_text, menu_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 20)))

            exit_text = self.hud_font.render("Press Q to Quit", True, (255, 255, 255))
            self.screen.blit(exit_text, exit_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 80)))

            for i in range(8):
                x = 120 + i * 140
                y = 120 + int(20 * math.sin(pygame.time.get_ticks() * 0.003 + i))
                sad_text = self.font.render(":(", True, (255, 120, 120))
                self.screen.blit(sad_text, sad_text.get_rect(center=(x, y)))
                
        # ------------------------------
        # MENU STATE
        # ------------------------------     

        elif self.state == GameState.MENU:

            mouse_pos = pygame.mouse.get_pos()

            title = self.font.render("Welcome to Memory Game",True,(255, 255, 255))

            self.screen.blit(title,title.get_rect(center=(settings.WIDTH // 2, 150)))

            # Button rects
            self.easy_rect = pygame.Rect(settings.WIDTH // 2 - 100, 220, 200, 45)
            self.medium_rect = pygame.Rect(settings.WIDTH // 2 - 100, 280, 200, 45)
            self.hard_rect = pygame.Rect(settings.WIDTH // 2 - 100, 340, 200, 45)
            self.start_rect = pygame.Rect(settings.WIDTH // 2 - 100, 440, 200, 55)

            def draw_button(rect, text, normal_color, hover_color, is_selected=False):

                hovered = rect.collidepoint(mouse_pos)
                draw_rect = rect.inflate(10, 8) if hovered else rect
                color = hover_color if hovered else normal_color

                pygame.draw.rect(self.screen, color, draw_rect, border_radius=12)

                if hovered:
                    pygame.draw.rect(self.screen, (255, 255, 255), draw_rect, 3, border_radius=12)

                if is_selected:
                    pygame.draw.rect(self.screen, (255, 255, 0), draw_rect, 3, border_radius=12)

                text_surface = self.hud_font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, text_surface.get_rect(center=draw_rect.center))
                """
                if is_selected:
                    check_text = self.hud_font.render("✓", True, (255, 255, 255))
                    self.screen.blit(check_text, (draw_rect.x + 15, draw_rect.centery - 10))
                    """

            draw_button(self.easy_rect, "Easy", (80,120,200), (120,170,255), self.difficulty == Difficulty.EASY)
            draw_button(self.medium_rect, "Medium", (80,120,200), (120,170,255), self.difficulty == Difficulty.MEDIUM)
            draw_button(self.hard_rect, "Hard", (80,120,200), (120,170,255), self.difficulty == Difficulty.HARD)
            draw_button(self.start_rect, "Start Game", (60,180,100), (90,230,140))

            marquee_text = self.hud_font.render("Boost Your Memory", True, (255, 255, 0))
            self.screen.blit(marquee_text, (self.marquee_x, settings.HEIGHT - 40))

             #isaret
            exit_text = self.hud_font.render("Press Q to Exit", True, (255, 255, 0))
            self.screen.blit(exit_text, exit_text.get_rect(center=(settings.WIDTH // 2, self.start_rect.bottom + 40)))

            for x, y, age in self.explosions:
                emoji_text = self.emoji_font.render("🧠✨", True, (255, 255, 255))
                self.screen.blit(emoji_text, (x, y))
                
        if self.state == GameState.PAUSED:

            pause_text = self.font.render("PAUSED", True, (255, 255, 0))     
            menu_text = self.font.render("Press M to return to Main Menu", True, (255, 255, 0))
            exit_text = self.font.render("Press Q to Exit Game", True, (255, 255, 0))
       
            self.screen.blit(pause_text, pause_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 80)))
            self.screen.blit(menu_text, menu_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 10)))
            self.screen.blit(exit_text, exit_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 70)))

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

        if self.state == GameState.MENU:
            self.marquee_x += 120 * dt
            if self.marquee_x > settings.WIDTH:
                self.marquee_x = -250
           
               
            self.explosion_timer += dt
            if self.explosion_timer >= 0.5:
                x = random.choice([random.randint(30, 180), random.randint(settings.WIDTH - 180, settings.WIDTH - 30)])
                y = random.randint(80, settings.HEIGHT - 100)
                self.explosions.append([x, y, 0])
                self.explosion_timer = 0

            for explosion in self.explosions:
                explosion[2] += dt

            self.explosions = [e for e in self.explosions if e[2] < 1.0]

            return
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
        if self.state == GameState.MENU:
            self.marquee_x -= 120 * dt
            if self.marquee_x < -250:
                self.marquee_x = settings.WIDTH

            self.explosion_timer += dt
            if self.explosion_timer >= 0.35:
                self.explosions.append([random.randint(50, settings.WIDTH - 50), random.randint(80, settings.HEIGHT - 120), 0])
                self.explosion_timer = 0

            for explosion in self.explosions:
                explosion[2] += dt

            self.explosions = [e for e in self.explosions if e[2] < 1.0]
            return
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
            # Cards match if their match_value is the same
            if self.first_card.match_value == self.second_card.match_value:

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
        self.board = Board(settings.WIDTH,settings.HEIGHT,self.board.rows,self.board.cols,self.difficulty)

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

        rows, cols = self.level_manager.get_current_level()

        self.board = Board(settings.WIDTH, settings.HEIGHT, rows, cols, self.difficulty)

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