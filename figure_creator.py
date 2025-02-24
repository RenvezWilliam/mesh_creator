import multiprocessing.process
import gmsh

from datetime import datetime
from typing import Literal

import creator

import multiprocessing

class FIGURE_CREATOR:
    def __init__(self):
        self.points  = []
        self.surface = None
        self.fig_id  = 0

        self.points.append([])
    
    def add_fig(self):
        self.points.append([])
        self.fig_id += 1

    def initialize(self):
        gmsh.initialize()
        gmsh.clear()
        gmsh.model.add("form")

    def add_point(self, x, y):
        self.points[self.fig_id].append(gmsh.model.geo.add_point(x, y, 0, 1))

    def create_surface(self):
        # Créer les lignes pour toutes les surfaces.

        
        lines = []
        for i in range(len(self.points)):
            lines.append([])
            for j in range(len(self.points[i]) - 1):        
                lines[i].append(gmsh.model.geo.addLine(self.points[i][j], self.points[i][j + 1]))
            lines[i].append(gmsh.model.geo.addLine(self.points[i][-1], self.points[i][0]))
            
            
        # Créer les loops pour chaque surfaces
        loops = []
        for i in range(len(lines)):
            loops.append(gmsh.model.geo.add_curve_loop(lines[i]))

        # Créer la surface à partir des loops
        surface = gmsh.model.geo.add_plane_surface(loops)

    def finilize(self, mode : Literal['tri', 'quad'], algorithm : int):
        if mode == 'quad':
            gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
        else:
            gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 0)
        
        gmsh.option.setNumber("Mesh.Algorithm", algorithm)

        ## Créer le maillage
        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(1)
        gmsh.model.mesh.generate(2)

    def view_mesh(self):
        gmsh.fltk.run()

    def save(self, filename):
        gmsh.write(filename+'.msh')
    
    def save_as_geo(self):
        # Sauvegarde // Devra être modifié lorsque les quarts de cercles seront en place
        dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Placement de tous les points
        id = 1

        with open(f'./figure_{dt}.geo', 'w') as f:
            for pts_list in self.points:
                for pt in pts_list:
                    f.write(f'Point({id}) = {{{pt[0]}, {pt[1]}, 0, 1.0}}')


##########################################################################

def automatize(points, mode: Literal['tri', 'quad'] = "tri", algorithm : int = 6):
    try :
        fc = FIGURE_CREATOR()
        fc.initialize()

        for i, pp in enumerate(points):
            
            for p in pp:
                p = (float(p[0] / 100), float(500 - p[1]/100))
                fc.add_point(p[0], p[1])
            
            if i != len(points) - 1:
                fc.add_fig()

        fc.create_surface()
        fc.finilize(mode, algorithm=algorithm)

        if mode == 'tri':
            fc.save(f"mesh_tri_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        else:
            fc.save(f"mesh_quad_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")

        return True
    
    except Exception as e:

        print(f"\033[1mLa sauvegarde n'est pas possible dù à une erreur : \033[91m{e}\033[0m")
        return False

def view(points, mode: Literal['tri', 'quad'] = "tri", game : creator.Game = None, algorithm : int = 6):
    try :
        if game == None:
            return

        fc = FIGURE_CREATOR()
        fc.initialize()

        for i, pp in enumerate(points):
            
            for p in pp:
                p = (float(p[0] / 100), float(500 - p[1]/100))
                fc.add_point(p[0], p[1])
            
            if i != len(points) - 1:
                fc.add_fig()

        fc.create_surface()
        fc.finilize(mode, algorithm = algorithm)

        game.display_switch(False)

        gmsh_process = multiprocessing.Process(target=fc.view_mesh)
        gmsh_process.start()
        gmsh_process.join()

        game.display_switch(True)

        return True
    
    except Exception as e:
        print(f"\033[1mLa visualisation n'est pas possible dù à une erreur : \033[91m{e}\033[0m")

        return False

def save_as_geo(points):
    fc = FIGURE_CREATOR()

    for i, pp in enumerate(points):
        
        for p in pp:
            p = (float(p[0] / 100), float(500 - p[1]/100))
            fc.add_point(p[0], p[1])
        
        if i != len(points) - 1:
            fc.add_fig()

    fc.save_as_geo()


##########################################################################

if __name__ == "__main__":
    """ Création d'une étoile """ # Obsolète

    # # Initialisation des Variables :
    # points = []
    # center_x, center_y = 2.5, 2.5
    # outer_radius = 2
    # inner_radius = 0.9
    # angle_offset = math.radians(90)

    # # Mise en place des points de l'étoile
    # for i in range(10):
    #     radius = outer_radius if i % 2 == 0 else inner_radius
    #     angle = angle_offset + i * math.pi / 5
    #     x = center_x + radius * math.cos(angle)
    #     y = center_y + radius * math.sin(angle)
    #     points.append((x, y))
    
    # automatize(points, 'tri') # Récupère un maillage triangulaire de l'étoile
    # automatize(points, 'quad') # Récupère un mallage quandrangulaire de l'étoile
