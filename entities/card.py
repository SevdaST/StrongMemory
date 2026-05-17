import pygame

#Card sınıfı oyundaki tek bir memory kartını temsil eder. Yani her kart için bu sınıftan bir nesne oluşturulur.
class Card:
    def __init__(self, value: int, rect: pygame.Rect): #value	kartın değeri (eşleşme için)**rect	kartın ekrandaki konumu
        """
        Represents a single memory card.
        value -> number used for matching
        rect  -> position and size of the card on the screen
        """
        self.is_hovered = False
        # Value used for matching cards later
        self.value = value

        # pygame.Rect that defines card position and size
        self.rect = rect

        # Card state flags
        self.is_flipped = False
        self.is_matched = False
        self.flip_animation = 0
        self.is_animating = False

    def contains_point(self, pos: tuple[int, int]) -> bool:  # bu metod kartın üstüne tıklanıp tıklanmadığını kontrol eder
        """
        Check if a mouse click is inside this card.
        """
        return self.rect.collidepoint(pos)

    def flip(self) -> None:
        """
        Flip the card (change its visible state).
        Matched cards should not flip again.
        """

        if self.is_matched:
            return

        # Toggle flip state
        self.is_flipped = not self.is_flipped
        self.is_animating = True
        self.flip_animation = 0

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:

        """
        Draw the card on the screen.

        There are 3 visual states:
        1) Face-down
        2) Face-up
        3) Matched
       *********** state-based rendering kullanılıyor.
        """
        draw_rect = self.rect.copy()

        if self.is_animating:         
            shrink = self.flip_animation
            draw_rect.width = max(10, self.rect.width - shrink)
            draw_rect.center = self.rect.center

        # If card is matched, draw color
        if self.is_matched:
            pygame.draw.rect(screen, (240, 230, 230), draw_rect)
            pygame.draw.rect(screen, (120, 120, 120), draw_rect, 2)
            return

        # Face-down card ***kapalı
        if not self.is_flipped:
            color = (70, 70, 70) if self.is_hovered else (40, 40, 40)

            border_color = (255, 255, 100) if self.is_hovered else (200, 200, 200)

            pygame.draw.rect(screen, color, draw_rect)
            pygame.draw.rect(screen, border_color, draw_rect, 2)

            return

        # Face-up card ***açık kart için border lı rect çiz içine de card value çiz
        pygame.draw.rect(screen, (252, 246, 245), draw_rect)   #(R,G,B) (255,255,255) max deger beyaz (0,0,0) min deger siyah
        pygame.draw.rect(screen, (20, 20, 20), draw_rect, 2)

        # Draw card value in the center
        text = font.render(str(self.value), True, (20, 20, 20))
        text_rect = text.get_rect(center=self.rect.center) #yazıyı kartın ortasına yazmak için

        screen.blit(text, text_rect) # varolan surface üzerine value surface i yazıyoruz. kart rect in üzerine text rect yazdırıyoruz

    def update(self, dt):

            if self.is_animating:

                self.flip_animation += 500 * dt

                if self.flip_animation >= self.rect.width:
                    self.flip_animation = self.rect.width
                    self.is_animating = False