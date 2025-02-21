import pygame
from pygame.locals import *
import sys

import figure_creator as fc

## Initialisation des couleurs ##
WHITE           = (255, 255, 255)
ANCHOR_BIG      = (100, 100, 100)
ANCHOR_NORMAL   = (150, 150, 150)
ANCHOR_SMALL    = (200, 200, 200)

CURRENT_POINT   = (100, 100, 255)
LAST_POINT      = (255, 200, 50)
CURRENT_LINE    = (200, 50, 255)
LAST_LINE       = (255, 50, 50)

OTHER_POINT     = (204, 152, 255)
OTHER_LINE      = (204, 152, 255)

class Game:

    def __init__(self):
        self.initialize()

        self._is_on                     = True
        self.figures                    = []
        self.figures.append(Figure())
        self.current_selected_figure    = 0
        self.algorithm                  = 5
    
    def initialize(self):
        pygame.init()
        self.size                       = self.width, self.height = 500, 500
        self.window                     = pygame.display.set_mode(self.size)
        self.clock                      = pygame.time.Clock().tick(30)
        self.title                      = pygame.display.set_caption('Editeur de figure')

        self._ctrl, self._shift         = False, False

    def refresh(self):
        self.window.fill(WHITE)

        if self._ctrl and not self._shift   : self.draw_large_anchor_lines()
        if not self._ctrl and self._shift   : self.draw_anchor_lines()
        if self._ctrl and self._shift       : self.draw_small_anchor_lines()

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
            self.figures[self.current_selected_figure].add_point(x, y)

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
            self.refresh()
            self.events()

            pygame.display.flip()

    def draw(self): # Pour toutes les figures, lance les dessins
        for i in range(len(self.figures)):
            self.figures[i].draw_points(self.window, False) if self.current_selected_figure != i else self.figures[i].draw_points(self.window, True)
            self.figures[i].draw_lines(self.window, False) if self.current_selected_figure != i else self.figures[i].draw_lines(self.window, True)

    def remove_last_point(self): ## IF NOT remove_last_point() pour la figure en cours -> regarde si on possède plus d'une figure. si oui, supprime la figure.
        if self.figures[self.current_selected_figure].remove_last_point():
            pass
        else:
            if len(self.figures) > 1:
                self.remove_current_figure()
                print('figure supprimée')
        
    def remove_current_figure(self):
        self.figures.pop(self.current_selected_figure)
        self.current_selected_figure = self.current_selected_figure % len(self.figures)

    def save(self):
        mode = "quad" if self._shift else "tri"

        self.remove_all_empty_figures()

        points = []

        for f in self.figures:
            points.append(f.points)
            if len(f.points) < 3:
                print('Une des surfaces possède moins de 3 points, il ne peut pas être sauvegardée')
                return
            
        fc.automatize(points=points, mode=mode, algorithm=(self.algorithm + 1))
    
    def view_mesh(self):
        mode = "quad" if self._shift else "tri"

        print(f"is shift on : {self._shift}")

        self.remove_all_empty_figures()

        points = []

        for f in self.figures:
            points.append(f.points)
            if len(f.points) < 3:
                print('Une des surfaces possède moins de 3 points, il ne peut pas être sauvegardée')
                return
        

        fc.view(points=points, mode=mode, game=self, algorithm=(self.algorithm + 1))

    
    def save_as_geo(self):

        self.remove_all_empty_figures()

        points = []

        for f in self.figures:
            points.append(f.points)
            if len(f.points) < 3:
                print('Une des surfaces possède moins de 3 points, il ne peut pas être sauvegardée')
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
        print("-======= MENU EXPLICATIF =======-")
        print('Points')
        print("• Clic gauche        -> Ajout d'un point")
        print("• Clic droit         -> Retire le dernier point de la figure")

        print("\nAncrage")
        print("• CTRL               -> Grand ancrage")
        print("• SHIFT              -> Ancrage Moyen")
        print("• CTRL + SHIFT       -> Petit ancrage")

        print("\nGestion des figures")
        print("• 'N'                -> Nouvelle figure")
        print("• '🠕'                -> Figure suivante")
        print("• '🠗'                -> Figure précédente")

        print("\nSauvegarde")
        print("• 'S'                -> Sauvegarde en .msh")
        print("• SHIFT + 'S'        -> Sauvegarde en .msh (avec subdivision)")

        print('\nVisualisation')
        print("• 'V'                -> Visualiser sous GMSH")
        print("• SHIFT + 'V'        -> Visualiser sous GMSH (avec subdivision)")

        print('\nAlgorithmes')
        print("• 'A'                -> Changer d'algorithme")

        print("\n\n•• 'H' pour revoir cette liste ••")


    def add_new_figure(self):
        self.figures.append(Figure())
        self.current_selected_figure = len(self.figures) - 1
    
    def next_figure(self):
        self.current_selected_figure = (self.current_selected_figure + 1) % (len(self.figures))

    def previous_figure(self):
        self.current_selected_figure = (self.current_selected_figure - 1) % (len(self.figures))

    def change_algorithm(self):
        self.algorithm = (self.algorithm + 1) % 11

        print('Algorithme sélectionné: ', end='')

        if self.algorithm == 0 : print("MeshAdapt")
        if self.algorithm == 1 : print("Automatic")
        if self.algorithm == 2 : print("Initial mesh only")
        if self.algorithm == 3 : self.algorithm += 1
        if self.algorithm == 4 : print("Delaunay")
        if self.algorithm == 5 : print("Frontal-Delaunay")
        if self.algorithm == 6 : print("BAMG")
        if self.algorithm == 7 : print("Frontal-Delaunay for Quads")
        if self.algorithm == 8 : print("Packing of Parallelograms")
        if self.algorithm == 9 : self.algorithm += 1
        if self.algorithm == 10 : print("Quasi-structured Quad")

    def events(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LSHIFT]: _shift = True

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == 'left shift'   : self._shift = True
                if pygame.key.name(event.key) == 'left ctrl'    : self._ctrl  = True
                if pygame.key.name(event.key) == 's'            : self.save()
                if pygame.key.name(event.key) == 'n'            : self.add_new_figure()
                if pygame.key.name(event.key) == 'up'           : self.next_figure()
                if pygame.key.name(event.key) == 'down'         : self.previous_figure()
                if pygame.key.name(event.key) == 'g'            : self.save_as_geo()
                if pygame.key.name(event.key) == 'v'            : self.view_mesh()
                if pygame.key.name(event.key) == 'h'            : self.show_help()
                if pygame.key.name(event.key) == 'a'            : self.change_algorithm()
            
            if event.type == pygame.KEYUP:
                if pygame.key.name(event.key) == 'left shift': self._shift = False
                if pygame.key.name(event.key) == 'left ctrl' : self._ctrl  = False

            if event.type == MOUSEBUTTONDOWN:

                if event.button == pygame.BUTTON_LEFT: ## PLACE UN POINT
                    x, y = pygame.mouse.get_pos()

                    if self._ctrl and not self._shift:
                        x = round(x / 100) * 100
                        y = round(y / 100) * 100

                    if not self._ctrl and self._shift:
                        x = round(x / 50) * 50
                        y = round(y / 50) * 50
                    
                    if self._ctrl and self._shift:
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
    
    def add_point(self, x, y):
        self.points.append((x, y))
    
    def remove_last_point(self) -> bool: # Si return False et que l'on souhaite retirer un point, on pourrait simplement détruire la figure avec la reception du False
        if len(self.points) == 0:
            return False

        self.points.pop(-1)
        return True
    
    def draw_points(self, window, current_figure: bool):

        if len(self.points) <= 0: # Il ne possède pas de points, donc pas de dessin, puni !
            return
        
        for i in range(len(self.points) - 1):
            pygame.draw.circle(window, CURRENT_POINT, self.points[i], 5) if current_figure else pygame.draw.circle(window, OTHER_POINT, self.points[i], 3)
        pygame.draw.circle(window, LAST_POINT, self.points[-1], 5) if current_figure else pygame.draw.circle(window, OTHER_POINT, self.points[-1], 3)

    def draw_lines(self, window, current_figure: bool):

        if len(self.points) <= 1: # Il ne possède pas assez de points, pas de ligne, encore puni !
            return
        
        for i in range(len(self.points) - 1):
            pygame.draw.line(window, CURRENT_LINE, self.points[i], self.points[i + 1], 2) if current_figure else pygame.draw.line(window, OTHER_LINE, self.points[i], self.points[i + 1], 2)
        pygame.draw.line(window, LAST_LINE, self.points[-1], self.points[0], 2) if current_figure else pygame.draw.line(window, OTHER_LINE, self.points[-1], self.points[0], 2)
            
if __name__ == '__main__':

    game = Game()

    print("• AFFICHER LE MENU EXPLICATIF -> 'H'")

    while True:
        game.display()