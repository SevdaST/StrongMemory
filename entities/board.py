import pygame
import random
from entities.card import Card
from core.difficulty import Difficulty


class Board:
    def __init__(self, screen_width, screen_height,rows,cols,difficulty=None):
        """
        The Board class is responsible for generating the grid layout
        and creating the Card objects placed on that grid.
        """
        """
       Board kartlarin sahadaki düzenini yönetir
            **kaç satir ve sütun olacağini bilmek**kartlarin ekranda nereye yerleşeceğini hesaplamak**her hücre için bir pygame.Rect oluşturmak
            bu rect'leri kullanarak Card nesneleri üretmek**kart değerlerini eşli şekilde oluşturup kariştirmak
        """

        total_cells = rows * cols

        # A memory game needs an even number of cards
        if total_cells % 2 != 0:
            raise ValueError("Board must contain an even number of cells.") #çift sayıda card olması kontrolü

        # Store grid dimensions
        self.rows = rows
        self.cols = cols

        # Margin between the grid and the window edges
        self.margin = 40

        # Space between cells
        self.spacing = 10

        self.difficulty = difficulty

        # Calculate the usable screen area for the grid
        usable_width = screen_width - (2 * self.margin)
        usable_height = screen_height - (2 * self.margin)

        # Calculate the maximum possible cell width and height
        cell_width = (usable_width - (cols - 1) * self.spacing) // cols
        cell_height = (usable_height - (rows - 1) * self.spacing) // rows

        # Ensure cells are square
        self.cell_size = min(cell_width, cell_height) #kare olacağı için min olan kenar uzunluğu seçiliyor

        # Total width and height of the grid #hücrelerin yerleşeceği grid boyutu
        grid_width = cols * self.cell_size + (cols - 1) * self.spacing
        grid_height = rows * self.cell_size + (rows - 1) * self.spacing

        # Center the grid on the screen
        self.start_x = (screen_width - grid_width) // 2
        self.start_y = (screen_height - grid_height) // 2

        # Store all cell rectangles  
        self.cells: list[pygame.Rect] = []
        self.create_cells()

        # Create shuffled card values and assign them to cards
        self.cards: list[Card] = []
        values = self.generate_card_values() # bu fonsiyon bir liste döndürür

        # to get two list use zip in phyton
        
        for rect, value_data in zip(self.cells, values):

            display_value, match_value = value_data

            card = Card(
                value=display_value,
                rect=rect,
                match_value=match_value
            )

            self.cards.append(card)

    def create_cells(self) -> None: 
        """
        Creates the grid cell rectangles.
        Each rectangle represents one card position.
        """
        self.cells.clear()

        for row in range(self.rows):
            for col in range(self.cols):
                x = self.start_x + col * (self.cell_size + self.spacing)
                y = self.start_y + row * (self.cell_size + self.spacing)

                rect = pygame.Rect(x, y,self.cell_size,self.cell_size,)

                self.cells.append(rect)

    def draw_layout_rects(self, screen: pygame.Surface) -> None:
        """
        Draws the grid rectangles
        """
        for rect in self.cells:
            pygame.draw.rect(screen, (200, 200, 200), rect, 2)
   
    def draw_hud_panel(self, screen: pygame.Surface) -> None:
        """Draws a background panel behind the HUD row."""
        panel_height = 36
        panel_margin = 10

        hud_rect = pygame.Rect(
            panel_margin,
            panel_margin,
            screen.get_width() - (panel_margin * 2),
            panel_height
        )

        pygame.draw.rect(screen, (25, 25, 25), hud_rect, border_radius=10)
        pygame.draw.rect(screen, (120, 120, 120), hud_rect, 2, border_radius=10)

    def draw_cards(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        padding_x = 20
        padding_y = 15

        board_rect = pygame.Rect(
            self.start_x - padding_x,
            self.start_y - padding_y,
            (self.cols * self.cell_size) + ((self.cols - 1) * self.spacing) + (padding_x * 2),
            (self.rows * self.cell_size) + ((self.rows - 1) * self.spacing) + (padding_y * 2)
        )

        pygame.draw.rect(screen, (25, 25, 25), board_rect, border_radius=16)
        pygame.draw.rect(screen, (120, 120, 120), board_rect, 3, border_radius=16)

        for card in self.cards:
            card.draw(screen, font)

    
    def generate_card_values(self):

        if self.difficulty == Difficulty.EASY:
            return self.create_easy_values()
        
        elif self.difficulty == Difficulty.MEDIUM:
            return self.create_medium_values()

        elif self.difficulty == Difficulty.HARD:
            return self.create_hard_values()

    def create_easy_values(self):

        pair_count = (self.rows * self.cols) // 2

        numbers = list(range(1, pair_count + 1)) * 2

        random.shuffle(numbers)

        return [(str(number), str(number)) for number in numbers]
   
    def create_medium_values(self):

        all_pairs = [
            ("3 + 5", "8"),
            ("10 - 4", "6"),
            ("2 x 3", "6"),
            ("12 / 4", "3"),
            ("7 + 2", "9"),
            ("5 x 2", "10"),
            ("15 - 7", "8"),
            ("18 / 3", "6"),
            ("4 + 9", "13"),
            ("6 x 2", "12"),
            ("20 - 5", "15"),
            ("16 / 4", "4"),
        ]

        total_cards = self.rows * self.cols
        num_pairs = total_cards // 2

        selected_pairs = all_pairs[:num_pairs]

        values = []

        for operation, result in selected_pairs:

            values.append((operation, result))
            values.append((result, result))

        random.shuffle(values)

        return values
   
    def create_hard_values(self):

        all_pairs = [
            ("🐦🌳", "bird_tree"),
            ("🐱🌙", "cat_moon"),
            ("🐶🏠", "dog_house"),
            ("🐟🌊", "fish_sea"),
            ("🦋🌸", "butterfly_flower"),
            ("🐝🌻", "bee_sunflower"),
            ("🌞🌴", "sun_tree"),
            ("🚗🛣️", "car_road"),
            ("🦁👑", "lion_king"),
            ("🐧❄️", "penguin_snow"),
            ("🌈☁️", "rainbow_cloud"),
            ("🍎📚", "apple_book"),
            ("🎵🎧", "music_headphones"),
            ("⚽🥅", "football_goal"),
            ("🚀🌌", "rocket_space"),
            ("🐢🌿", "turtle_leaf"),
        ]
        total_cards = self.rows * self.cols
        num_pairs = total_cards // 2

        selected_pairs = all_pairs[:num_pairs]

        values = []

        for display, match_value in selected_pairs:
            values.append((display, match_value))
            values.append((display, match_value))

        random.shuffle(values)

        return values
    #metod(self):::::Buradaki self metodun hangi nesne üzerinde çalıştığını gösterir. nesnenin içindeki değişkenlere erişmeyi sağlar
    #Python’da class metodlarının ilk parametresi olur