import pygame
import math
from pygame.locals import *
import sys
import json

from tool.button import Button
from geometry.figure import Figure
from geometry.arc import Arc

from saver import Saver
from reader import Reader

## Initialisation des couleurs ##
WHITE               = (255, 255, 255)
OPTIONS             = (230, 230, 255)
OPTIONS_TITLE       = (100, 100, 255)
OPTIONS_VALUE       = (100, 100, 140)
WARNING             = (200, 150, 0)
SLIDER              = (50, 50, 50)
SLIDER_BALL         = (100, 100, 255)

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

DRAG                = (50, 255, 50)

BOUTON              = (180, 180, 255) 

class Game:
    def __init__(self):
        self.mode                       = "line"
        self.ancrage                    = 0
        self._is_on                     = True
        self.figures: list[Figure]      = []
        self.figures.append(Figure())
        self.current_selected_figure    = 0
        self.algorithm                  = 5
        self.had_error                  = False
        self.dragging                   = False
        self.point_dragged              = None
        self.element_size               = 1.0
        self.subdivised                 = False

        self.buttons: list[Button]      = []

        ## Paramètres de la fenêtre ##
        self.algo_title_coo             = (600, 15)
        self.algo_value_coo             = (600, 35)
        self.algo_warn_coo              = (600, 50)

        self.subd_title_coo             = (600, 70)
        self.subd_value_coo             = (600, 85)

        self.element_title_coo          = (600, 105)
        self.element_value_coo          = (600, 120)      
        self.element_size_slider_coo    = [600, 135]
        
        self.figure_title_coo           = (600, 200)
        self.figure_value_coo           = (600, 215)

        self.mode_title_coo             = (600, 235)
        self.mode_value_coo             = (600, 250)

        self.ancrage_title_coo          = (600, 270)
        self.ancrage_value_coo          = (600, 285)

        

       
        
        self.is_sliding_element_size    = False

        with open("config_touches.json", 'r', encoding= "utf-8") as f:
            self.touches = json.load(f)

        self.initialize()
    
    def initialize(self):
        pygame.init()

        self.buttons = []
        self.buttons.append(Button((675, 5, 20, 20), ">", lambda: self.change_algorithm(True)))
        self.buttons.append(Button((505, 5, 20, 20), "<", lambda: self.change_algorithm(False)))
        self.buttons.append(Button((675, 60, 20, 20), ">", lambda: self.change_subdivision()))

        self.buttons.append(Button((505, 190, 20, 20), "<", lambda: self.previous_figure()))
        self.buttons.append(Button((675, 190, 20, 20), ">", lambda: self.next_figure()))
        self.buttons.append(Button((650, 190, 20, 20), "+", lambda: self.add_new_figure()))
        self.buttons.append(Button((675, 225, 20, 20), ">", lambda: self.change_mode()))
        self.buttons.append(Button((505, 260, 20, 20), "<", lambda: self.change_anchor(False)))
        self.buttons.append(Button((675, 260, 20, 20), ">", lambda: self.change_anchor(True)))

        self.buttons.append(Button((510, 425, 180, 20), "Voir avec GMSH", lambda: self.view_mesh()))
        self.buttons.append(Button((510, 450, 180, 20), "Sauvegarder en .msh", lambda: self.save_as_msh()))
        self.buttons.append(Button((510, 475, 180, 20), "Sauvegarder en .geo", lambda: self.save_as_geo()))
        

        self.size                   = self.width, self.height = 700, 500
        self.window                 = pygame.display.set_mode(self.size)
        self.clock                  = pygame.time.Clock().tick(30)
        self.title                  = pygame.display.set_caption(f'Editeur de figure GMSH')

        self._ctrl, self._shift     = False, False


    def refresh(self):
        self.window.fill(WHITE)        

        # Dessine les encrages
        if self.ancrage == 1: self.draw_large_anchor_lines()
        if self.ancrage == 2: self.draw_anchor_lines()
        if self.ancrage == 3: self.draw_small_anchor_lines()

        self.draw()
        self.draw_options()
    
    def draw_options(self):
        option = "Ligne" if self.mode == "line" else "Arc de cercle"
        ancrage = "Grand" if self.ancrage == 1 else "Moyen" if self.ancrage == 2 else "Petit" if self.ancrage == 3 else "Aucun"
        figure = f"{self.current_selected_figure + 1} / {len(self.figures)}"
        subdivision = "Activé" if self.subdivised else "Désactivé"

        ## Dessin du background des options
        pygame.draw.rect(self.window, OPTIONS, (500, 0, 200, 500))

        ## Chargement des différentes polices
        font_title  = pygame.font.Font(None, 25)
        font        = pygame.font.Font(None, 20)

        ## Intialisation des textes
        algo_titre = font_title.render("Algorithme", True, OPTIONS_TITLE, (220, 220, 255))
        algo = font.render(self.get_algo_name(), True, OPTIONS_VALUE, (220, 220, 255))
        algo_warn = font.render("Expérimental", True, WARNING, (220, 220, 255))

        element_title = font_title.render("Taille Éléments", True, OPTIONS_TITLE, (220, 220, 255))
        element_value = font.render(str(round(self.element_size, 2)), True, OPTIONS_VALUE, (220, 220, 255))

        point_mode_title = font_title.render(f"Mode", True, OPTIONS_TITLE, (220, 220, 255))
        point_mode       = font.render(option, True, OPTIONS_VALUE, (220, 220, 255))

        ancrage_title = font_title.render(f"Ancrage", True, OPTIONS_TITLE, (220, 220, 255))
        ancrage_value = font.render(ancrage, True, OPTIONS_VALUE, (220, 220, 255))

        figure_title = font_title.render(f"Figure", True, OPTIONS_TITLE, (220, 220, 255))
        figure_value = font.render(figure, True, OPTIONS_VALUE, (220, 220, 255))

        subdivision_title = font_title.render(f"Subdivision", True, OPTIONS_TITLE, (220, 220, 255))
        subdivision_value = font.render(subdivision, True, OPTIONS_VALUE, (220, 220, 255))

        ## Dessine les boutons
        for button in self.buttons:
            button.draw(self.window)

        ## Affiche le texte

        # Algorithme
        self.window.blit(algo_titre, self.get_text_center(algo_titre, self.algo_title_coo))
        self.window.blit(algo, self.get_text_center(algo, self.algo_value_coo))
        if self.algorithm >= 6 :
            self.window.blit(algo_warn, self.get_text_center(algo_warn, self.algo_warn_coo))
        
        # Subdivision
        self.window.blit(subdivision_title, self.get_text_center(subdivision_title, self.subd_title_coo))
        self.window.blit(subdivision_value, self.get_text_center(subdivision_value, self.subd_value_coo))

        # Element Size
        self.window.blit(element_title, self.get_text_center(element_title, self.element_title_coo))
        self.window.blit(element_value, self.get_text_center(element_value, self.element_value_coo))
        
        # Dessine le slider
        pygame.draw.line(self.window, SLIDER, (520, self.element_size_slider_coo[1]), (680, self.element_size_slider_coo[1]))
        pygame.draw.circle(self.window, SLIDER_BALL, (self.element_size_slider_coo[0], self.element_size_slider_coo[1]), 5)

        # Dessine le séparateur
        pygame.draw.line(self.window, (200, 200, 255), (500, 170), (700, 170))

        # Point Mode
        self.window.blit(point_mode_title, self.get_text_center(point_mode_title, self.mode_title_coo))
        self.window.blit(point_mode, self.get_text_center(point_mode, self.mode_value_coo))

        # Ancrage
        self.window.blit(ancrage_title, self.get_text_center(ancrage_title, self.ancrage_title_coo))
        self.window.blit(ancrage_value, self.get_text_center(ancrage_value, self.ancrage_value_coo))

        # Figures
        self.window.blit(figure_title, self.get_text_center(figure_title, self.figure_title_coo))
        self.window.blit(figure_value, self.get_text_center(figure_value, self.figure_value_coo))

        
    
    def get_text_center(self, text, coordinates):
        txt_rct = text.get_rect()
        txt_rct.center = coordinates
        return txt_rct
    
    def get_algo_name(self) -> str:
        if self.algorithm == 0 : return "MeshAdapt"
        if self.algorithm == 1 : return "Automatic"
        if self.algorithm == 2 : return "Initial mesh only"
        if self.algorithm == 4 : return "Delaunay"
        if self.algorithm == 5 : return "Frontal-Delaunay"
        if self.algorithm == 6 : return "BAMG"
        if self.algorithm == 7 : return "Frontal-Delaunay for Quads"
        if self.algorithm == 8 : return "Packing of Parallelograms"
        if self.algorithm == 10 : return "Quasi-structured Quad"

        return "None"

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

    def left_clicked(self):
        for p in self.figures[self.current_selected_figure].points:
            if p.is_hovered():
                self.point_dragged = p
                self.dragging = True
                return
        
        for f in self.figures[self.current_selected_figure].forms:
            if f.is_hovered():
                self.figures[self.current_selected_figure].create_center_point()
                return

        x, y = pygame.mouse.get_pos()

        x, y = self.get_anchor_coords(x, y)

        self.add_point(x, y)
            
    def stop_dragging(self):
        if self.point_dragged == None: return
        x, y = pygame.mouse.get_pos()
        x, y = self.get_anchor_coords(x, y)

        if 0 > x:   x = 0
        if x > 500: x = 500

        if 0 > y:   y = 0
        if y > 500: y = 500

        self.point_dragged.move_to(x, y)

        for f in self.figures[self.current_selected_figure].forms:
            if not isinstance(f, Arc): continue

            if self.point_dragged in (f.p1, f.p2, f.pc):
                f.relocate_center()


        self.dragging = False
        self.point_dragged = None

    def add_point(self, x, y):
        is_present = False
        for points in self.figures[self.current_selected_figure].points:
            if points.x == x and points.y == y and self.mode == "line":
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
            self.options()
            self.refresh()

            pygame.display.flip()

    def options(self):
        self.element_size_slider()
    
    def element_size_slider(self):
        if not self.is_sliding_element_size: return

        x, y = pygame.mouse.get_pos()

        if not ((510 < x < 690) and (self.element_size_slider_coo[1] - 10 < y < self.element_size_slider_coo[1] + 10)):
            self.is_sliding_element_size = False
        
        self.element_size_slider_coo[0] = x
        if self.element_size_slider_coo[0] < 520 : self.element_size_slider_coo[0] = 520
        if self.element_size_slider_coo[0] > 680 : self.element_size_slider_coo[0] = 680

        slider_x = self.element_size_slider_coo[0] - 520

        # 10 ^ (x / 80) / 10
        self.element_size = ( 10 ** (slider_x / 80) ) / 10

    def draw(self): 
        # Pour toutes les figures, lance les dessins
        for i in range(len(self.figures)):
            self.figures[i].display(self.window, False) if self.current_selected_figure != i else self.figures[i].display(self.window, True)
        
        if not self.dragging: return
        x, y = pygame.mouse.get_pos()

        x, y = self.get_anchor_coords(x, y)

        pygame.draw.circle(self.window, DRAG, (x, y), 5)
            
    def get_anchor_coords(self, x, y) -> tuple:
        if self.ancrage == 1:
            x = round(x / 100) * 100
            y = round(y / 100) * 100

        if self.ancrage == 2:
            x = round(x / 50) * 50
            y = round(y / 50) * 50
        
        if self.ancrage == 3:
            x = round(x / 10) * 10
            y = round(y / 10) * 10
        
        return (x, y)

    def remove_point(self): ## IF NOT remove_last_point() pour la figure en cours -> regarde si on possède plus d'une figure. si oui, supprime la figure.
        if len(self.figures[self.current_selected_figure].points) == 0:
            if len(self.figures) > 1 : self.remove_current_figure()
            return

        self.figures[self.current_selected_figure].remove_hovered_point()
        
    def remove_current_figure(self):
        self.figures.pop(self.current_selected_figure)
        self.current_selected_figure = self.current_selected_figure % len(self.figures)

    def save_as_msh(self):
        saver = Saver()
        
        if self.had_error:
            print("Vous ne pouvez plus sauvegarder qu'en .geo à cause d'une erreur précédente.")
            return

        self.remove_all_empty_figures()

        points = []

        for f in self.figures:
            points.append(f.points)
            if len(f.points) < 3:
                print('Une des surfaces possède moins de 3 points, il ne peut pas être sauvegardée')
                return
            
        if not saver.save_mesh(self.figures, self.subdivised, (self.algorithm + 1), self.element_size):
            self.had_error = True
        

    def view_mesh(self):
        saver = Saver()

        if self.had_error:
            print("Vous ne pouvez plus visualiser à cause d'une erreur précédente.")
            return

        ok = False
        for f in self.figures:
            if len(f.points) >= 2:
                ok = True

            if len(f.points) == 1:
                print('Une des surfaces possède moins de 2 points, il ne peut pas être visualisée')
                return
            
        if not ok:
            print("Vous ne pouvez pas visualiser une figure sans points.")
            return

        self.remove_all_empty_figures()

        for f in self.figures:
            if len(f.points) < 2:
                print('Une des surfaces possède moins de 2 points, il ne peut pas être sauvegardée')
                return

        if not saver.view(figs=self.figures, is_subdivised=self.subdivised, game=self, algorithm=(self.algorithm + 1), element_size=self.element_size):
            self.had_error = True

    def save_as_geo(self):
        saver = Saver()
        self.remove_all_empty_figures()
        for f in self.figures:
            if len(f.points) < 2:
                print('Une des surfaces possède moins de 2 points, il ne peut pas être sauvegardée')
                return

        saver.save_geo(self.figures)

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
        print(f"• '{self.touches['save_as_geo']}'                -> Sauvegarder la forme")
        print(f"• '{self.touches['view_in_gmsh']}'                -> Visualiser sous GMSH")

        print(f'{BLEUC}{ITALIQUE}Algorithmes{RESET}')
        print(f"• '{self.touches['change_algorithm']}'                -> Changer d'algorithme")
        print(f"• '{self.touches['change_subdivision']}'                -> Activer / Désactiver la subdivision")

        print(f"\n{ITALIQUE}•• '{self.touches['show_help']}' pour revoir cette liste ••{RESET}")

    def add_new_figure(self):
        self.figures.append(Figure())
        self.current_selected_figure = len(self.figures) - 1
    
    def next_figure(self):
        self.current_selected_figure = (self.current_selected_figure + 1) % (len(self.figures))

    def previous_figure(self):
        self.current_selected_figure = (self.current_selected_figure - 1) % (len(self.figures))
    
    def change_subdivision(self):
        self.subdivised = not self.subdivised

    def change_algorithm(self, next=None):
        if next == None:
            self.algorithm = (self.algorithm + 1) % 11 if not self._shift else (self.algorithm - 1) % 11

            if self.algorithm == 3 : self.algorithm = (self.algorithm + 1) if not self._shift else (self.algorithm - 1)
            if self.algorithm == 9 : self.algorithm = (self.algorithm + 1) if not self._shift else (self.algorithm - 1)
        else:
            if next == True:
                self.algorithm = (self.algorithm + 1) % 11

                if self.algorithm == 3 : self.algorithm = (self.algorithm + 1)
                if self.algorithm == 9 : self.algorithm = (self.algorithm + 1)

            if next == False:
                self.algorithm = (self.algorithm - 1) % 11

                if self.algorithm == 3 : self.algorithm = (self.algorithm - 1)
                if self.algorithm == 9 : self.algorithm = (self.algorithm - 1)

        
    
    def change_mode(self):
        if self.mode == "line":
            self.mode = "arc"
        elif self.mode == "arc":
            self.mode = "line"

        if self.figures[self.current_selected_figure]._choosing_arc_center:
            self.figures[self.current_selected_figure]._choosing_arc_center = False
            self.figures[self.current_selected_figure].remove_point(self.figures[self.current_selected_figure].points[-1])
    
    def change_anchor(self, next=None):
        if next == None:
            self.ancrage = (self.ancrage + 1) % 4 if not self._shift == True else (self.ancrage - 1) % 4
        else:
            if next == True:
                self.ancrage = (self.ancrage + 1) % 4

            if next == False:
                self.ancrage = (self.ancrage - 1) % 4

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
                if pygame.key.name(event.key) == self.touches["save_as_mesh"]       : self.save_as_msh()
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
                x, y = pygame.mouse.get_pos()

                if event.button == pygame.BUTTON_LEFT: ## CLIC GAUCHE
                    if 0 < x < 500 and 0 < y < 500:
                        self.left_clicked()
                    
                    for button in self.buttons:
                        button.clicked()

                    if 510 < x < 690 and self.element_size_slider_coo[1] - 10 < y < self.element_size_slider_coo[1] + 10:
                        self.is_sliding_element_size = True
                    return
                    
                if event.button == pygame.BUTTON_RIGHT: ## RETIRE LE DERNIER POINT
                    if 0 < x < 500 and 0 < y < 500:
                        self.remove_point()
                    return
            
            if event.type == MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    if self.dragging : self.stop_dragging()
                    if self.is_sliding_element_size : self.is_sliding_element_size = False

    

def run(path : str = None):
    game = Game()
    game.show_help()

    if path is not None:
        try:
            rd = Reader()
            forms = rd.read(path)
            game.figures = forms
            game.current_selected_figure = 0

        except Exception as e:
            print(f"Lancement de l'éditeur sans lecture de fichier : \033[91m{e}\033[0m")
    
    while True:
        game.display()

if __name__ == '__main__':
    run()
    #run("result_example/geo_unrolled/1-sliced_square.geo_unrolled")

    