import pygame
import math
from geometry.point import Point

DEFAULT         = (200, 50, 255)
UNFOCUSED       = (204, 152, 255)
HOVER           = (255, 0, 0)

class Line:
    def __init__(self, p1: Point, p2: Point, id: float):
        self.p1 = p1
        self.p2 = p2
        self.id = id
    
    def display(self, screen :pygame.Surface, is_last: bool, current_fig: bool):

        if not current_fig:
            pygame.draw.line(screen, UNFOCUSED, (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), 1)
            return

        if self.is_hovered():
            pygame.draw.line(screen, HOVER, (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), 2)
            return

        pygame.draw.line(screen, DEFAULT, (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), 2)
    
    def is_hovered(self, tolerance: float = 4) -> bool:
        return self.distance_mouse_line() <= tolerance
    
    def distance_mouse_line(self) -> float:
        x, y = pygame.mouse.get_pos()

        # Vecteur AB et AP
        ABx, ABy = self.p2.x - self.p1.x, self.p2.y - self.p1.y
        APx, APy = x - self.p1.x, y - self.p1.y
        AB_len_sq = ABx**2 + ABy**2

        t = 0 if AB_len_sq == 0 else max(0, min(1, (APx*ABx + APy*ABy) / AB_len_sq))

        # Projection du point P sur le segment
        proj_x, proj_y = self.p1.x + t*ABx, self.p1.y + t*ABy

        return math.sqrt((x - proj_x)**2 + (y - proj_y)**2)
    
    def center(self) -> tuple:
        return (self.p1.x + self.p2.x) / 2, (self.p1.y + self.p2.y) / 2