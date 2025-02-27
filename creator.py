import pygame
import math
from pygame.locals import *
import sys
import json

import figure_creator as fc

""" 
FINIR : Create_surface dans figure_creator
+ Finir sauvegarde + visualisation
+ Faire sauvegarde .geo
"""


## Initialisation des couleurs ##
WHITE               = (255, 255, 255)
ANCHOR_BIG          = (100, 100, 100)
ANCHOR_NORMAL       = (150, 150, 150)
ANCHOR_SMALL        = (200, 200, 200)

CURRENT_POINT       = (100, 100, 255)
LAST_POINT          = (255, 200, 50)
CURRENT_LINE        = (200, 50, 255)
LAST_LINE           = (255, 50, 50)
CURRENT_ARC_POINT   = (224, 152, 255)
ARC_PREVIEW         = (255, 153, 255)

OTHER_POINT         = (204, 152, 255)
OTHER_LINE          = (204, 152, 255)
OTHER_ARC_POINT     = (230, 250, 255)

class Game:

    def __init__(self):
        self.mode                       = "ligne"
        self.ancrage                    = 0
        self._is_on                     = True
        self.figures                    = []
        self.figures.append(Figure())
        self.current_selected_figure    = 0
        self.algorithm                  = 5
        self.had_error                  = False

        with open("config_touches.json", 'r', encoding= "utf-8") as f:
            self.touches = json.load(f)

        self.initialize()
    
    def initialize(self):
        pygame.init()

        self.size                   = self.width, self.height = 500, 500
        self.window                 = pygame.display.set_mode(self.size)
        self.clock                  = pygame.time.Clock().tick(30)
        self.title                  = pygame.display.set_caption(f'Editeur de figure ({self.mode})')

        self._ctrl, self._shift     = False, False


    def refresh(self):
        self.window.fill(WHITE)

        # Dessine les encrages
        if self.ancrage == 1: self.draw_large_anchor_lines()
        if self.ancrage == 2: self.draw_anchor_lines()
        if self.ancrage == 3: self.draw_small_anchor_lines()

        self.draw()
    
    def draw_large_anchor_lines(self):
        for i in range(0, 500, 100):
            pygame.draw.line(self.window, ANCHOR_BIG, (0, i), (500, i))
            pygame.draw.line(self.window, ANCHOR_BIG, (i, 0), (i, 500))

    def draw_anchor_lines(self):
        for i in range(0, 500, 50):
            pygame.draw.line(self.window, ANCHOR_NORMAL, (0, i), (500, i))
            pygame.draw.line(self.window, ANCHOR_NORMAL, (i, 0), (i, 500))
            
            self.draw_large_anchor_lines()

    def draw_small_anchor_lines(self):
        for i in range(0, 500, 10):
            pygame.draw.line(self.window, ANCHOR_SMALL, (0, i), (500, i))
            pygame.draw.line(self.window, ANCHOR_SMALL, (i, 0), (i, 500))

            self.draw_anchor_lines()

    def add_point(self, x, y):
        is_present = False
        for points in self.figures[self.current_selected_figure].points:
            if points[0] == x and points[1] == y:
                is_present = True
        
        if not is_present:
            self.figures[self.current_selected_figure].add_point(x, y, self.mode)

    def display_switch(self, _on : bool = None):
        if _on == None:
            self._is_on = not self._is_on
        else:
            self._is_on = _on

        if self._is_on:
            self.initialize()
        else:
            pygame.quit()

    def display(self):
        if self._is_on:
            self.events()
            self.refresh()

            pygame.display.flip()

    def draw(self): 
        # Pour toutes les figures, lance les dessins
        for i in range(len(self.figures)):
            for i in range(len(self.figures)):
                self.figures[i].draw(self.window, False) if self.current_selected_figure != i else self.figures[i].draw(self.window, True)

    def remove_last_point(self): ## IF NOT remove_last_point() pour la figure en cours -> regarde si on possède plus d'une figure. si oui, supprime la figure.
        if not self.figures[self.current_selected_figure].remove_last_point():
            if len(self.figures) > 1:
                self.remove_current_figure()
                print('figure supprimée')
        
    def remove_current_figure(self):
        self.figures.pop(self.current_selected_figure)
        self.current_selected_figure = self.current_selected_figure % len(self.figures)

    def save(self):

        if self.had_error:
            print("Vous ne pouvez plus sauvegarder qu'en .geo à cause d'une erreur précédente.")
            return

        mode = "quad" if self._shift else "tri"

        self.remove_all_empty_figures()

        points = []

        for f in self.figures:
            points.append(f.points)
            if len(f.points) < 3:
                print('Une des surfaces possède moins de 3 points, il ne peut pas être sauvegardée')
                return
            
        if not fc.save_as_msh(self.figures, mode=mode, algorithm=(self.algorithm + 1)):
            self.had_error = True
    
    def view_mesh(self):

        if self.had_error:
            print("Vous ne pouvez plus visualiser à cause d'une erreur précédente.")
            return


        mode = "quad" if self._shift else "tri"

        self.remove_all_empty_figures()

        points = []

        for f in self.figures:
            points.append(f.points)
            if len(f.points) < 2:
                print('Une des surfaces possède moins de 2 points, il ne peut pas être sauvegardée')
                return
        

        if not fc.view(figs=self.figures, mode=mode, game=self, algorithm=(self.algorithm + 1)):
            self.had_error = True

    
    def save_as_geo(self):
        self.remove_all_empty_figures()

        points = []

        for f in self.figures:
            points.append(f.points)
            if len(f.points) < 2:
                print('Une des surfaces possède moins de 2 points, il ne peut pas être sauvegardée')
                return

        fc.save_as_geo(self.figures)

    def remove_all_empty_figures(self):
        while True:
            still_have_empty_figures = False
            for i, f in enumerate(self.figures):
                if len(f.points) == 0:
                    self.figures.pop(i)
                    still_have_empty_figures = True
                    break
            
            if not still_have_empty_figures:
                break
            
            self.current_selected_figure = 0

    def show_help(self):
        RESET       = '\033[0m'
        GRAS        = '\033[1m'
        ITALIQUE    =' \033[3m'
        BLEU        = '\033[34m'
        BLEUC       = '\033[94m'


        print(f"{BLEU}{GRAS}-======= MENU EXPLICATIF =======-{RESET}")
        print(f'{BLEUC}{ITALIQUE}Points{RESET}')
        print("• Clic gauche        -> Ajout d'un point")
        print("• Clic droit         -> Retire le dernier point de la figure")
        print(f"• '{self.touches['change_mode']}'                -> Changer mode (ligne / arc)")

        print(f"{BLEUC}{ITALIQUE}Ancrage{RESET}")
        print(f"• '{self.touches['change_anchor']}'                -> Changer d'ancrage (Aucun -> Grand -> Moyen -> Petit)")
        print(f"• SHIFT + '{self.touches['change_anchor']}'        -> Changer d'ancrage (Petit -> Moyen -> Grand -> Aucun)")

        print(f"{BLEUC}{ITALIQUE}Gestion des figures{RESET}")
        print(f"• '{self.touches['new_figure']}'                -> Nouvelle figure")
        print(f"• '{self.touches['next_figure']}'               -> Figure suivante")
        print(f"• '{self.touches['previous_figure']}'             -> Figure précédente")

        print(f"{BLEUC}{ITALIQUE}Sauvegarde{RESET}")
        print(f"• '{self.touches['save_as_mesh']}'                -> Sauvegarder le maillage")
        print(f"• SHIFT + '{self.touches['save_as_mesh']}'        -> Sauvegarder le maillage (avec subdivision)")
        print(f"• '{self.touches['save_as_geo']}'                -> Sauvegarder la forme")

        print(f'{BLEUC}{ITALIQUE}Visualisation{RESET}')
        print(f"• '{self.touches['view_in_gmsh']}'                -> Visualiser sous GMSH")
        print(f"• SHIFT + '{self.touches['view_in_gmsh']}'        -> Visualiser sous GMSH (avec subdivision)")

        print(f'{BLEUC}{ITALIQUE}Algorithmes{RESET}')
        print(f"• '{self.touches['change_algorithm']}'                -> Changer d'algorithme")

        print(f"\n{ITALIQUE}•• '{self.touches['show_help']}' pour revoir cette liste ••{RESET}")


    def add_new_figure(self):
        self.figures.append(Figure())
        self.current_selected_figure = len(self.figures) - 1
    
    def next_figure(self):
        self.current_selected_figure = (self.current_selected_figure + 1) % (len(self.figures))

    def previous_figure(self):
        self.current_selected_figure = (self.current_selected_figure - 1) % (len(self.figures))

    def change_algorithm(self):
        self.algorithm = (self.algorithm + 1) % 11 if not self._shift else (self.algorithm - 1) % 11

        print('Algorithme sélectionné: ', end='')

        if self.algorithm == 3 : self.algorithm = (self.algorithm + 1) if not self._shift else (self.algorithm - 1)
        if self.algorithm == 9 : self.algorithm = (self.algorithm + 1) if not self._shift else (self.algorithm - 1)
        
        if self.algorithm == 0 : print("MeshAdapt")
        if self.algorithm == 1 : print("Automatic")
        if self.algorithm == 2 : print("Initial mesh only")
        if self.algorithm == 4 : print("Delaunay")
        if self.algorithm == 5 : print("Frontal-Delaunay")
        if self.algorithm == 6 : print("BAMG")
        if self.algorithm == 7 : print("Frontal-Delaunay for Quads")
        if self.algorithm == 8 : print("Packing of Parallelograms")
        if self.algorithm == 10 : print("Quasi-structured Quad")
    
    def change_mode(self):
        if self.mode == "ligne":
            self.mode = "arc de cercle"
        elif self.mode == "arc de cercle":
            self.mode = "ligne"

        if self.figures[self.current_selected_figure]._choosing_arc_center:
            self.figures[self.current_selected_figure]._choosing_arc_center = False
            self.remove_last_point()


        self.title == pygame.display.set_caption(f'Editeur de figure ({self.mode})')
    
    def change_anchor(self):
        self.ancrage = (self.ancrage + 1) % 4 if not self._shift == True else (self.ancrage - 1) % 4

    def events(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LSHIFT]: _shift = True

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == 'left shift'                       : self._shift = True
                if pygame.key.name(event.key) == 'left ctrl'                        : self._ctrl  = True
                if pygame.key.name(event.key) == self.touches["save_as_mesh"]       : self.save()
                if pygame.key.name(event.key) == self.touches["new_figure"]         : self.add_new_figure()
                if pygame.key.name(event.key) == self.touches["next_figure"]        : self.next_figure()
                if pygame.key.name(event.key) == self.touches["previous_figure"]    : self.previous_figure()
                if pygame.key.name(event.key) == self.touches["save_as_geo"]        : self.save_as_geo()
                if pygame.key.name(event.key) == self.touches["view_in_gmsh"]       : self.view_mesh()
                if pygame.key.name(event.key) == self.touches["show_help"]          : self.show_help()
                if pygame.key.name(event.key) == self.touches["change_algorithm"]   : self.change_algorithm()
                if pygame.key.name(event.key) == self.touches["change_mode"]        : self.change_mode()
                if pygame.key.name(event.key) == self.touches["change_anchor"]      : self.change_anchor()
                if pygame.key.name(event.key) == self.touches["save_as_geo"]        : self.save_as_geo()

            
            if event.type == pygame.KEYUP:
                if pygame.key.name(event.key) == 'left shift'   : self._shift = False
                if pygame.key.name(event.key) == 'left ctrl'    : self._ctrl  = False

            if event.type == MOUSEBUTTONDOWN:

                if event.button == pygame.BUTTON_LEFT: ## PLACE UN POINT
                    x, y = pygame.mouse.get_pos()

                    if self.ancrage == 1:
                        x = round(x / 100) * 100
                        y = round(y / 100) * 100

                    if self.ancrage == 2:
                        x = round(x / 50) * 50
                        y = round(y / 50) * 50
                    
                    if self.ancrage == 3:
                        x = round(x / 10) * 10
                        y = round(y / 10) * 10

                    self.add_point(x, y)
                    return

                if event.button == pygame.BUTTON_RIGHT: ## RETIRE LE DERNIER POINT
                    self.remove_last_point()
                    return

class Figure:

    def __init__(self):
        self.points = []
        self.points_arc = []
        self.lines  = []
        self.arc = []
        self.order = []
        
        self.arc_save = None

        self._choosing_arc_center = False
    
    def add_point(self, x, y, mode):
        if not self._choosing_arc_center: self.points.append((x, y))

        if len(self.points) < 2: return # ne peut pas dessiner de lignes ou d'arc de cercle car il n'y a que 0 ou 1 point

        if mode == 'ligne':
            self.lines.append( (len(self.points) - 2, len(self.points) - 1) )
            self.order.append('line')
        elif mode == 'arc de cercle':
            if not self._choosing_arc_center:
                self.arc_save = (len(self.points) - 2, len(self.points) - 1)
                self._choosing_arc_center = True
            else :
                self.add_arc(self.arc_save, (x, y))
                self.order.append('arc')
                self._choosing_arc_center = False

    def add_arc(self, points, center):
        s_ = self.points[points[0]]
        e_ = self.points[points[1]]
        c_ = center


        # Si a (et b) sont None, c'est que les deux points sont l'un au dessus de l'autre.
        a = (e_[1] - s_[1]) / (e_[0] - s_[0]) if e_[0] != s_[0] else None
        b = s_[1] - (a * s_[0]) if a is not None else None

        ctr = ((s_[0] + e_[0]) /2, (s_[1] + e_[1]) /2)

        # Droite perpendiculaire à la fonc. affine
        a_ = - (1 / a) if (a is not None) and (a != 0) else None
        b_ = ctr[1] - (a_ * ctr[0]) if a_ is not None else None

        cx_star = (a_ * (c_[1] - b_) + c_[0]) / ((a_**2) + 1) if a_ is not None else None
        cy_star = (a_ * cx_star + b_) if a_ is not None else None

        
        if a_ is not None:
            c_star = (cx_star, cy_star)
        else:
            if s_[0] == e_[0]:
                c_star = (center[0] , ctr[1])
            if s_[1] == e_[1]:
                c_star = (ctr[0] , center[1])
        
        self.points_arc.append(c_star)
        self.arc.append((points, (len(self.points_arc) - 1)))

    
    def remove_last_point(self) -> bool: # Si return False et que l'on souhaite retirer un point, on pourrait simplement détruire la figure avec la reception du False
        if len(self.points) == 0:
            return False
        
        ok = False
        while not ok:
            ok = True
            if len(self.lines) > 0:
                for i, line in enumerate(self.lines):
                    if line[0] == len(self.points) - 1:
                        ok = False
                        self.lines.pop(i)
                        self.order.pop(-1)
                        break
                    if line[1] == len(self.points) - 1:
                        ok = False
                        self.lines.pop(i)
                        self.order.pop(-1)
                        break
            
            if len(self.arc) > 0:
                for i, arc in enumerate(self.arc):
                    if arc[0][0] == len(self.points) - 1:
                        ok = False
                        self.points_arc.pop(arc[1])
                        self.arc.pop(i)
                        self.order.pop(-1)
                        break
                    if arc[0][1] == len(self.points) - 1:
                        ok = False
                        self.points_arc.pop(arc[1])
                        self.arc.pop(i)
                        self.order.pop(-1)
                        break

        self.points.pop(-1)

        return True
    
    def draw(self, window, current_figure: bool):
        self.draw_points(window, current_figure)
        self.draw_arc_points(window, current_figure)
        self.draw_lines(window, current_figure)
        self.draw_arc(window, current_figure)
        if self._choosing_arc_center:
            self.draw_arc_preview(window, current_figure)
    
    def draw_arc_points(self, window, current_figure: bool):
        if len(self.points_arc) == 0: return

        for i in range(len(self.points_arc)):
            pygame.draw.circle(window, CURRENT_ARC_POINT, self.points_arc[i], 4) if current_figure else pygame.draw.circle(window, OTHER_ARC_POINT, self.points_arc[i], 2)

    def draw_points(self, window, current_figure: bool):

        if len(self.points) == 0:return # Il ne possède pas de points, donc pas de dessin, puni !
            
        
        for i in range(len(self.points) - 1):
            pygame.draw.circle(window, CURRENT_POINT, self.points[i], 5) if current_figure else pygame.draw.circle(window, OTHER_POINT, self.points[i], 3)
        pygame.draw.circle(window, LAST_POINT, self.points[-1], 5) if current_figure else pygame.draw.circle(window, OTHER_POINT, self.points[-1], 3)

    def draw_lines(self, window, current_figure: bool):
        
        if len(self.points) > 1 : pygame.draw.line(window, LAST_LINE, self.points[-1], self.points[0], 2) if current_figure else pygame.draw.line(window, OTHER_LINE, self.points[-1], self.points[0], 2)

        if len(self.lines) == 0: return # Pas de lignes ? pas de dessin !
            
        for i in range(len(self.lines)):
            line = self.lines[i]
            pygame.draw.line(window, CURRENT_LINE, self.points[line[0]], self.points[line[1]], 2) if current_figure else pygame.draw.line(window, OTHER_LINE, self.points[line[0]], self.points[line[1]], 2)
        

    def draw_arc_preview(self, window, current_figure: bool):
        s_ = self.points[-2]
        e_ = self.points[-1]
        c_ = pygame.mouse.get_pos()


        # Si a (et b) sont None, c'est que les deux points sont l'un au dessus de l'autre.
        a = (e_[1] - s_[1]) / (e_[0] - s_[0]) if e_[0] != s_[0] else None
        b = s_[1] - (a * s_[0]) if a is not None else None

        ctr = ((s_[0] + e_[0]) /2, (s_[1] + e_[1]) /2)

        # Droite perpendiculaire à la fonc. affine
        a_ = - (1 / a) if (a is not None) and (a != 0) else None
        b_ = ctr[1] - (a_ * ctr[0]) if a_ is not None else None

        cx_star = (a_ * (c_[1] - b_) + c_[0]) / ((a_**2) + 1) if a_ is not None else None
        cy_star = (a_ * cx_star + b_) if a_ is not None else None

        
        if a_ is not None:
            c_star = (cx_star, cy_star)
        else:
            if s_[0] == e_[0]:
                c_star = (c_[0] , ctr[1])
            if s_[1] == e_[1]:
                c_star = (ctr[0] , c_[1])

        radius = math.sqrt( (c_star[0] - s_[0])**2 + (c_star[1] - s_[1])**2 )

        s_a = math.atan2( - (s_[1] - c_star[1]), s_[0] - c_star[0])
        e_a = math.atan2( - (e_[1] - c_star[1]), e_[0] - c_star[0])

        delta = (e_a - s_a) % (2 * math.pi)

        if delta > math.pi:
            s_a, e_a = e_a, s_a
            
        rect = pygame.Rect(c_star[0] - radius, c_star[1] - radius, 2 * radius, 2 * radius)

        pygame.draw.arc(window, ARC_PREVIEW, rect, s_a, e_a, 1)
        

    def draw_arc(self, window, current_figure: bool):
        for arc in self.arc:
            
            s_ = self.points[arc[0][0]] # Start
            e_ = self.points[arc[0][1]] # End
            c_ = self.points_arc[arc[1]]# Center

            radius = math.sqrt((c_[0] - s_[0])**2 + (c_[1] - s_[1])**2)

            s_a = math.atan2(- (s_[1] - c_[1]), s_[0] - c_[0])
            e_a = math.atan2(- (e_[1] - c_[1]), e_[0] - c_[0])

            delta = (e_a - s_a) % (2 * math.pi)
            if delta > math.pi: # On veut dessiner le moins possible (prendre le plus petit côté)
                s_a, e_a = e_a, s_a

            rect = pygame.Rect(c_[0] - radius, c_[1] - radius, 2 * radius, 2 * radius)

            pygame.draw.arc(window, CURRENT_LINE, rect, s_a, e_a, 2) if current_figure else pygame.draw.arc(window, OTHER_LINE, rect, s_a, e_a, 1)
        
if __name__ == '__main__':

    game = Game()

    print(f"• AFFICHER LE MENU EXPLICATIF -> 'H'")

    while True:
        game.display()