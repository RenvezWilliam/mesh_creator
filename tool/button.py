from typing import Callable, Tuple
import pygame

TEXT_COLOR       = (100, 100, 140)
BUTTON_COLOR     = (180, 180, 255)
BUTTON_HOVERED   = (140, 140, 255)

class Button:
    def __init__(self, rect: Tuple[int, int, int, int], texte: str, action: Callable[[], None]):
        self.rect = pygame.Rect(rect)
        self.text = texte
        self.action = action
    
    def draw(self, surface: pygame.Surface):
        # Dessine le rectangle
        pygame.draw.rect(surface, BUTTON_HOVERED, self.rect, border_radius=5) if self.is_hovered() else pygame.draw.rect(surface, BUTTON_COLOR, self.rect, border_radius=5)

        font = pygame.font.Font(None, 22)
        text_surface = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)
    
    def clicked(self):
        if self.is_hovered():
            self.action()