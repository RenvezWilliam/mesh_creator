import pygame

DEFAULT         = (100, 100, 255)
LAST            = (255, 200, 50)
UNFOCUSED       = (204, 152, 255)
HOVER           = (255, 0, 0)

ARC             = (224, 152, 255)
UNFOCUSED_ARC   = (230, 250, 255)

class Point:
    def __init__(self, x, y, id: float, is_arc_point=False):
        self.x = x
        self.y = y
        self.id = id
        self.is_arc_point = is_arc_point
    
    def __eq__(self, other):
        if isinstance(other, Point):
            return (self.id == other.id) and (self.x == other.x) and (self.y == other.y)

    def display(self, screen :pygame.Surface, is_last: bool, current_fig: bool):

        if self.is_arc_point:

            if not current_fig:
                pygame.draw.circle(screen, UNFOCUSED_ARC, (self.x, self.y), 5)
                return
            
            pygame.draw.circle(screen, ARC, (self.x, self.y), 5)
            return
            
        if not current_fig:
            pygame.draw.circle(screen, UNFOCUSED, (self.x, self.y), 5)
            return

        if self.is_hovered():
            pygame.draw.circle(screen, HOVER, (self.x, self.y), 5)
            return
        
        if is_last:
            pygame.draw.circle(screen, LAST, (self.x, self.y), 5)
            return

        pygame.draw.circle(screen, DEFAULT, (self.x, self.y), 5)
    
    def is_hovered(self) -> bool:
        x, y = pygame.mouse.get_pos()
        tolerance = 5.0
        # Si la distance de la souris est inférieure à la tolérance, renvois true, sinon false
        return ((x - self.x)**2 + (y - self.y)**2)**0.5 < tolerance
    
    def move_to(self, x, y):
        self.x = x
        self.y = y


