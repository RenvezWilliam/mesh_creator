import pygame
import math

from geometry.point import Point
from geometry.arc import Arc
from geometry.line import Line

ARC_PREVIEW = (255, 153, 255)
LAST_LINE   = (255, 150, 150)
UNFOCUSED   = (204, 152, 255)

class Figure:
    def __init__(self):
        self.points : list[Point] = []
        self.forms = []
        self._choosing_arc_center = False
        self.arc_save = None

    def add_point(self, x, y, mode):
        new_id_pt = 0 if len(self.points) == 0 else self.points[-1].id + 1
        self.points.append(Point(x, y, new_id_pt))

        if len(self.points) < 2: return
        
        new_id_form = 0 if len(self.forms) == 0 else self.forms[-1].id + 1

        if mode == "line":
            self.add_line(new_id_form)
        elif mode == "arc":
            self.add_arc(new_id_form)
    
    def add_line(self, new_id):
        last_valid_points = [p for p in self.points if not p.is_arc_point][-2:]
        self.forms.append(Line(last_valid_points[0], last_valid_points[1], len(self.forms)))

    def add_arc(self, new_id):
        if not self._choosing_arc_center:
            last_valid_points = [p for p in self.points if not p.is_arc_point][-2:]

            self.arc_save = (last_valid_points[0], last_valid_points[1])
            self._choosing_arc_center = True
        else:
            s_ = self.arc_save[0]
            e_ = self.arc_save[1]
            c_ = self.points[-1]

            # si a (et b) sont None, c'est que les deux points sont l'un au dessus de l'autre.
            a = (e_.y - s_.y) / (e_.x - s_.x) if e_.x != s_.x else None
            b = s_.y - a * s_.x if a is not None else None

            ctr = ((s_.x + e_.x)  / 2, (s_.y + e_.y) / 2)

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
            
            self.points[-1].move_to(c_star[0], c_star[1])
            self.points[-1].is_arc_point = True

            self.forms.append(Arc(self.arc_save[0], self.arc_save[1], self.points[-1], new_id))
            self._choosing_arc_center = False

    def remove_hovered_point(self):
        for p in self.points:
            if p.is_hovered() and not p.is_arc_point:
                self.remove_point(p)
    
    def remove_point(self, p: Point):
        

        if self._choosing_arc_center:
            self._choosing_arc_center = False
            self.remove_point(None)

        index = -1
        for i, pt in enumerate(self.points):
            if pt == p:
                index = i
                break
        self.points.pop(index)

        # On retire les deux formes qui étaient liés avec le point
        points : list[Point] = []
        id = None
        ok = False

        while not ok:
            ok = True
            for i, f in enumerate(self.forms):
                if f.p1 == p:
                    points.append(f.p2)
                    id = self.forms[i].id
                    self.forms.pop(i)

                    if isinstance(f, Arc):
                        self.remove_point(f.pc)

                    ok = False
                    break
                if f.p2 == p:
                    points.append(f.p1)
                    id = self.forms[i].id
                    self.forms.pop(i)

                    if isinstance(f, Arc):
                        self.remove_point(f.pc)

                    ok = False
                    break

        # On replace les deux formes par une ligne reliant les deux
        if len(points) == 2:
                self.forms.append(Line(points[0], points[1], id))

    def display(self, screen, current_figure: bool):
        for f in self.forms: f.display(screen, False, current_figure)
        
        last_point = 0
        for i, p in enumerate(self.points): # cherche l'index du dernier point
            if not p.is_arc_point : last_point = i

        for i, p in enumerate(self.points): 
            if i != last_point : p.display(screen, False, current_figure)
            else : p.display(screen, True, current_figure)
            
        
        if self._choosing_arc_center: self.display_arc_preview(screen)
        self.draw_last_line(screen ,current_figure)
        
    def draw_last_line(self, screen, current_figure):
        if len(self.points) < 2: return
 
        p1 = self.points[0]
        p2 = [p for p in self.points if not p.is_arc_point][-1:][0]

        if current_figure:
            pygame.draw.line(screen, LAST_LINE, (p1.x, p1.y), (p2.x, p2.y), 2)
        else:
            pygame.draw.line(screen, UNFOCUSED, (p1.x, p1.y), (p2.x, p2.y), 1)

    def display_arc_preview(self, screen):
        s_ = self.arc_save[0]
        e_ = self.arc_save[1]
        c_ = pygame.mouse.get_pos()

        a = (e_.y - s_.y) / (e_.x - s_.x) if e_.x != s_.x else None
        b = s_.y - (a * s_.x)

        ctr = ((s_.x + e_.x) / 2, (s_.y + e_.y) / 2)

        a_ = - (1 / a) if (a is not None) and (a != 0) else None
        b_ = ctr[1] - (a_ * ctr[0]) if a_ is not None else None

        cx_star = (a_ * (c_[1] - b_) + c_[0]) / ((a_**2) + 1) if a_ is not None else None
        cy_star = (a_ * cx_star + b_) if a_ is not None else None

        if a_ is not None:
            c_star = (cx_star, cy_star)
        else:
            if s_.x == e_.x:
                c_star = (c_[0], ctr[1])
            if s_.y == e_.y:
                c_star = (ctr[0], c_[1])

        radius = math.sqrt( (c_star[0] - s_.x)**2 + (c_star[1] - s_.y)**2 )

        s_a = math.atan2( - (s_.y - c_star[1]), s_.x - c_star[0] )
        e_a = math.atan2( - (e_.y - c_star[1]), e_.x - c_star[0])

        delta = (e_a - s_a) % (2 * math.pi)

        if delta > math.pi:
            s_a, e_a = e_a, s_a

        rect = pygame.Rect(c_star[0] - radius, c_star[1] - radius, 2 * radius, 2 * radius)

        pygame.draw.arc(screen, ARC_PREVIEW, rect, s_a, e_a, 1)
    
    def create_center_point(self):

        for i, f in enumerate(self.forms):
            if f.is_hovered():
                point_id = (f.p1.id + f.p2.id) / 2
                
                p1 = f.p1
                p2 = f.p2
                center = f.center()
                form_id = f.id
                is_line = True if isinstance(f, Line) else False

                # Retire ligne ou arc + créer point
                self.forms.pop(i)
                np = Point(center[0], center[1], point_id, False)
                self.points.append(np)

                if is_line:
                    self.forms.append(Line(p1, np, form_id))
                    self.forms.append(Line(np, p2, form_id + 0.5))
                else:
                    # nouveau centre pour le second arc
                    nc = Point(f.pc.x, f.pc.y,f.pc.id + 0.5, True)
                    self.points.append(nc)
                    f.pc.id = p1.id + 0.75
                    a1 = Arc(p1, np, f.pc, form_id)
                    a2 = Arc(np, p2, nc, form_id + 0.5)
                    
                    a1.relocate_center()
                    a2.relocate_center()

                    self.forms.append(a1)
                    self.forms.append(a2)
                break
        
        self.remake_ids()

    def remake_ids(self):
        self.points.sort(key=lambda p :p.id)
        for i, p in enumerate(self.points) :
            p.id = i
        
        self.forms.sort(key=lambda f :f.id)
        for i, f in enumerate(self.forms):
            f.id = i

    def move_point(self, x, y, p : Point):
        if not p in self.points:
            return

        if not p.is_arc_point:
            p.move_to(x, y)
        else:
            pass
