import pygame


class Card:
    def __init__(self, value: int, rect: pygame.Rect):
        """
        Represents a single memory card.

        value -> number used for matching
        rect  -> position and size of the card on the screen
        """

        # Value used for matching cards later
        self.value = value

        # pygame.Rect that defines card position and size
        self.rect = rect

        # Card state flags
        self.is_flipped = False
        self.is_matched = False

    def contains_point(self, pos: tuple[int, int]) -> bool:
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

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """
        Draw the card on the screen.

        There are 3 visual states:
        1) Face-down
        2) Face-up
        3) Matched
        """

        # If card is matched, draw it in dim color
        if self.is_matched:
            pygame.draw.rect(screen, (70, 70, 70), self.rect)
            pygame.draw.rect(screen, (120, 120, 120), self.rect, 2)
            return

        # Face-down card
        if not self.is_flipped:
            pygame.draw.rect(screen, (40, 40, 40), self.rect)
            pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
            return

        # Face-up card
        pygame.draw.rect(screen, (220, 220, 220), self.rect)
        pygame.draw.rect(screen, (20, 20, 20), self.rect, 2)

        # Draw card value in the center
        text = font.render(str(self.value), True, (20, 20, 20))
        text_rect = text.get_rect(center=self.rect.center)

        screen.blit(text, text_rect)