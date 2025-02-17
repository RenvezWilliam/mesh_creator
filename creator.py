import pygame
from pygame.locals import *
import sys

import gmsh_creator as gc

class Game:

    def __init__(self):
        pygame.init()
        self.size                   = self.width, self.height = 500, 500
        self.window                 = pygame.display.set_mode(self.size)
        self.clock                  = pygame.time.Clock().tick(30)

        ## Initialisation des couleurs ##
        self.WHITE                  = (255, 255, 255)
        self.ANCHOR_BIG             = (100, 100, 100)
        self.ANCHOR_NORMAL          = (150, 150, 150)
        self.ANCHOR_SMALL           = (200, 200, 200)
        self.POINT                  = (100, 100, 255)
        self.LAST_POINT             = (255, 200, 50)
        self.LINE                   = (200, 50, 255)
        self.LAST_LINE              = (255, 50, 50)

        ## Initialisation des variables ##
        self._ctrl, self._shift     = False, False
        self.points                 = []

    def refresh(self):
        self.window.fill(self.WHITE)

        if self._ctrl and not self._shift   : self.draw_large_anchor_lines()
        if not self._ctrl and self._shift   : self.draw_anchor_lines()
        if self._ctrl and self._shift       : self.draw_small_anchor_lines()

        self.draw_lines()
        self.draw_points()
    
    def draw_large_anchor_lines(self):
        for i in range(0, 500, 100):
            pygame.draw.line(self.window, self.ANCHOR_BIG, (0, i), (500, i))
            pygame.draw.line(self.window, self.ANCHOR_BIG, (i, 0), (i, 500))

    def draw_anchor_lines(self):
        for i in range(0, 500, 50):
            pygame.draw.line(self.window, self.ANCHOR_NORMAL, (0, i), (500, i))
            pygame.draw.line(self.window, self.ANCHOR_NORMAL, (i, 0), (i, 500))
            
            self.draw_large_anchor_lines()

    def draw_small_anchor_lines(self):
        for i in range(0, 500, 10):
            pygame.draw.line(self.window, self.ANCHOR_SMALL, (0, i), (500, i))
            pygame.draw.line(self.window, self.ANCHOR_SMALL, (i, 0), (i, 500))

            self.draw_anchor_lines()



    def draw_points(self):
        if (len(self.points) > 0):
            for i in range(len(self.points) - 1):
                pygame.draw.circle(self.window, self.POINT, self.points[i], 5)
            pygame.draw.circle(self.window, self.LAST_POINT, self.points[-1], 5)

    def draw_lines(self):
        if (len(self.points) > 1):
            for i in range(len(self.points) - 1):
                pygame.draw.line(self.window, self.LINE, self.points[i], self.points[i + 1], 2)
            pygame.draw.line(self.window, self.LAST_LINE, self.points[-1], self.points[0], 2)

    def remove_last_point(self):
        if len(self.points) > 0:
            self.points.pop(-1)

    def save(self, mode = 'tri'):
        if len(self.points) < 3:
            print("Vous avez besoin d'au moins 3 points pour sauvegarder.")
            return
        gc.automatize(self.points, mode)

    def events(self):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LSHIFT]: _shift = True

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == 'left shift': self._shift = True
                if pygame.key.name(event.key) == 'left ctrl' : self._ctrl  = True
                if pygame.key.name(event.key) == 'r'         : self.remove_last_point()
                if pygame.key.name(event.key) == 't'         : self.save("tri")
                if pygame.key.name(event.key) == 'y'         : self.save("quad")
            
            if event.type == pygame.KEYUP:
                if pygame.key.name(event.key) == 'left shift': self._shift = False
                if pygame.key.name(event.key) == 'left ctrl' : self._ctrl  = False

            if event.type == MOUSEBUTTONDOWN:
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

                is_present = False
                for p in self.points:
                    if p == (x, y): is_present = True
                        
                if not is_present : self.points.append((x, y))

            
if __name__ == '__main__':

    game = Game()

    print("-======= MENU EXPLICATIF =======-\n")
    print("• Clique souris          -> Ajout de point")
    print("• Maintenir CTRL         -> Grand Ancrage")
    print("• Maintenir SHIFT        -> Moyen Ancrage")
    print("• Maintenir SHIFT + CTRL -> Petit Ancrage")
    print("• Bouton 'R'             -> Retire le dernier point")
    # print("• Bouton 'S'             -> Sauvegarder en un fichier MSH")
    print("• Bouton 'T'             -> Sauvegarder un fichier MSH avec un maillage triangulaire")
    print("• Bouton 'Y'             -> Sauvegarder un fichier MSH avec un maillage quadrangulaire")

    while True:
        game.refresh()
        game.events()

        pygame.display.flip()