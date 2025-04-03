import pygame
import math
from geometry.point import Point

DEFAULT         = (200, 50, 255)
# LAST            = (255, 50, 50)
UNFOCUSED       = (204, 152, 255)
HOVER           = (255, 0, 0)

class Arc:
    def __init__(self, p1: Point, p2: Point, pc: Point, id: float):
        self.p1 = p1
        self.p2 = p2
        self.pc = pc
        self.id = id

        self.s_a = None # Start Angle
        self.e_a = None # End Angle

    def display(self, screen :pygame.Surface, is_last: bool = False, current_fig: bool = False):
        if not current_fig:
            self.draw_arc(screen, UNFOCUSED, 1)
            return
        
        if self.is_hovered():
            self.draw_arc(screen, HOVER, 2)
            return
        
        self.draw_arc(screen, DEFAULT, 2)

    def draw_arc(self, screen: pygame.Surface, color: tuple, width: int):
        s_ = self.p1.x, self.p1.y
        e_ = self.p2.x, self.p2.y
        c_ = self.pc.x, self.pc.y

        radius = math.sqrt((s_[0] - c_[0])**2 + (s_[1] - c_[1])**2)

        s_a = math.atan2(- (s_[1] - c_[1]), s_[0] - c_[0])
        e_a = math.atan2(- (e_[1] - c_[1]), e_[0] - c_[0])

        delta = (e_a - s_a) % (2 * math.pi)
        if delta > math.pi:
            s_a, e_a = e_a, s_a
        
        self.s_a = s_a
        self.e_a = e_a
        
        rect = pygame.Rect(c_[0] - radius, c_[1] - radius, 2 * radius, 2 * radius)
        pygame.draw.arc(screen, color, rect, s_a, e_a, width)

    def is_hovered(self, tolerance = 5.0) -> bool:
        
        if self.s_a is None or self.e_a is None : return False

        # regarde si la souris se trouve dans le cercle, entre les deux points
        radius          = math.dist((self.pc.x, self.pc.y), (self.p1.x, self.p1.y))
        mouse_radius    = math.dist((self.pc.x, self.pc.y), pygame.mouse.get_pos())

        if not (radius - tolerance/2 <= mouse_radius <= radius + tolerance/2): return False
        
        theta_mouse = math.atan2(- (pygame.mouse.get_pos()[1] - self.pc.y), (pygame.mouse.get_pos()[0] - self.pc.x))

        theta_mouse = (theta_mouse + 2 * math.pi) % (2 * math.pi)

        s_a = self.s_a
        e_a = self.e_a

        if e_a < s_a:
            e_a += 2 * math.pi
        if theta_mouse < s_a:
            theta_mouse += 2 * math.pi
        
        return s_a <= theta_mouse <= e_a

        # if theta_start < theta_end:
        #     return theta_start <= theta_mouse <= theta_end
        # else:
        #     return theta_mouse >= theta_start or theta_mouse <= theta_end
    
    def relocate_center(self):
        # si un des points bouge, il faut absolument que le point central puisse se replacer
        s_ = self.p1
        e_ = self.p2
        c_ = self.pc

        # si a (et b) sont None, c'est que les deux points sont l'un au dessus de l'autre.
        a = (e_.y - s_.y) / (e_.x - s_.x) if e_.x != s_.x else None

        ctr = ((s_.x + e_.x) / 2, (s_.y + e_.y) / 2)

        a_ = - (1 / a) if a is not None and a != 0 else None
        b_ = ctr[1] - (a_ * ctr[0]) if a_ is not None else None

        cx_star = (a_ * (c_.y - b_) + c_.x) / ((a_**2) + 1) if a_ is not None else None
        cy_star = (a_ * cx_star + b_) if a_ is not None else None

        if a_ is not None:
            c_star = (cx_star, cy_star)
        else:
            if s_.x == e_.x:
                c_star = (c_.x, ctr[1])
            if s_.y == e_.y:
                c_star = (ctr[0], c_.y)

        self.pc.move_to(c_star[0], c_star[1])

    def center(self) -> tuple:
        radius = math.sqrt((self.p1.x - self.pc.x)**2 + (self.p1.y - self.pc.y)**2)

        s_a = self.s_a
        e_a = self.e_a

        if e_a < s_a:
            e_a += 2 * math.pi

        mid_a = (s_a + e_a) / 2

        mid_x = self.pc.x + radius * math.cos(mid_a)
        mid_y = self.pc.y - radius * math.sin(mid_a)

        return int(mid_x), int(mid_y)