import pygame
import random
from entities.card import Card


class Board:
    def __init__(self, screen_width: int, screen_height: int, rows: int, cols: int):
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
        for rect, value in zip(self.cells, values): #zip fonksiyonu iki seriyi birleştirmeye yarar
            card = Card(value=value, rect=rect)
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

    def draw_cards(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """
        Draw every card on the board.
        """
        for card in self.cards:
            card.draw(screen, font) # başka bir sınıfa ait olan metod çalıştırılır. yukarıda import edilen card sınıfının draw fonksiyonu

    def generate_card_values(self) -> list[int]: # herbirinden bir çift olacak şekilde rect sayısı kadar card value üretir
        """
        Generates pairs of values for the memory game
        and shuffles them randomly.
        """
        total_cards = self.rows * self.cols
        num_pairs = total_cards // 2

        values = []

        for i in range(1, num_pairs + 1): #range(start, stop),start ≤ i < stop, o yuzden +1 alındı
            values.append(i)
            values.append(i)

        random.shuffle(values) #Bu fonksiyon listeyi rastgele karıştırır. random kütüphanesinden gelir.
        return values
    
    #metod(self):::::Buradaki self metodun hangi nesne üzerinde çalıştığını gösterir. nesnenin içindeki değişkenlere erişmeyi sağlar
    #Python’da class metodlarının ilk parametresi olur