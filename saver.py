import multiprocessing.process
import gmsh

from datetime import datetime
from typing import Literal

import editor

from editor import Figure

import multiprocessing

class SAVER:
    def __init__(self):
        self.points     = []
        self.points_arc = []
        self.lines      = []
        self.arcs       = []
        self.surface    = None
        self.fig_id     = 0

        self.points.append([])
        self.points_arc.append([])
        self.lines.append([])
        self.arcs.append([])
    
    def add_fig(self):
        self.fig_id = self.fig_id + 1
        self.points.append([])
        self.points_arc.append([])
        self.lines.append([])
        self.arcs.append([])
        

    def initialize(self):
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.clear()
        gmsh.model.add("form")

    def add_point(self, x, y):
        self.points[self.fig_id].append(gmsh.model.geo.add_point(x, y, 0, 1))
    
    def add_point_arc(self, x, y):
        self.points_arc[self.fig_id].append(gmsh.model.geo.add_point(x, y, 0, 1))
    
    def add_line(self, line):
        self.lines[self.fig_id].append(gmsh.model.geo.addLine(self.points[self.fig_id][line[0]], self.points[self.fig_id][line[1]]))

    def add_arc(self, arc):
        self.arcs[self.fig_id].append(gmsh.model.geo.addCircleArc(self.points[self.fig_id][arc[0][0]], self.points_arc[self.fig_id][arc[1]], self.points[self.fig_id][arc[0][1]]))

    def create_surface(self):
        loops = []

        for i in range(self.fig_id + 1):
            
            self.lines[i].append(gmsh.model.geo.addLine(self.points[i][-1], self.points[i][0])) # Ajout de la dernière ligne

            form = sorted(self.lines[i] + self.arcs[i]) # Créer la forme avec les ID des lignes et arcs de cercles remise dans l'ordre

            loops.append(gmsh.model.geo.addCurveLoop(form))
  
        surface = gmsh.model.geo.addPlaneSurface(loops)
    

    def finilize(self, mode : Literal['tri', 'quad'] = 'tri', algorithm : int = 6):
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
        gmsh.write(filename+'.geo_unrolled')
    
    def save_as_geo(self, filename):
        gmsh.write(filename+'.geo_unrolled')
                

        

##########################################################################

def save_as_msh(figs : list[Figure], mode: Literal['tri', 'quad'] = "tri", algorithm : int = 6):
    sv = SAVER()
    sv.initialize()

    
    for i, fig in enumerate(figs):

        ## Ajouter les points un à un
        for pt in fig.points:
            pt = (float(pt[0] / 100), float((500 - pt[1]) / 100))
            sv.add_point(pt[0], pt[1])

        ## Ajouter les points arc un à un
        for pta in fig.points_arc:
            pta = (float(pta[0] / 100), float((500 - pta[1]) / 100))
            sv.add_point_arc(pta[0], pta[1])

        l, a = 0, 0
        ## Ajouter les lignes et les arcs dans l'ordre
        for j in range(len(fig.order)):
            if fig.order[j] == 'line':
                sv.add_line(fig.lines[l])
                l += 1
            elif fig.order[j] == 'arc':
                sv.add_arc(fig.arc[a])
                a += 1

        ## S'il reste des figures -> créer une nouvelle figure
        if i < len(figs) - 1:
            sv.add_fig()

    ## Créer la/les surface(s) puis finaliser
    sv.create_surface()

    ## save selon le mode
    sv.finilize(mode, algorithm = algorithm)

    if mode == 'tri':
        sv.save(f"mesh_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    else:
        sv.save(f"mesh_sub_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        
    return True
    

def view(figs : list[Figure], mode: Literal['tri', 'quad'] = "tri", game : editor.Game = None, algorithm : int = 6):
    
    if game == None:
        return

    sv = SAVER()
    sv.initialize()

    for i, fig in enumerate(figs):
        ## Ajouter les points un à un
        for pt in fig.points:
            pt = (float(pt[0] / 100), float((500 - pt[1]) / 100))
            sv.add_point(pt[0], pt[1])

        ## Ajouter les points arc un à un
        for pta in fig.points_arc:
            pta = (float(pta[0] / 100), float((500 - pta[1]) / 100))
            sv.add_point_arc(pta[0], pta[1])

        l, a = 0, 0
        ## Ajouter les lignes et les arcs dans l'ordre
        for j in range(len(fig.order)):
            if fig.order[j] == 'line':
                sv.add_line(fig.lines[l])
                l += 1
            elif fig.order[j] == 'arc':
                sv.add_arc(fig.arc[a])
                a += 1

        ## S'il reste des figures -> créer une nouvelle figure
        if i < len(figs) - 1:
            sv.add_fig()

    ## Créer la/les surface(s) puis finaliser
    sv.create_surface()

    ## save selon le mode
    sv.finilize(mode, algorithm = algorithm)

    game.display_switch(False)

    gmsh_process = multiprocessing.Process(target=sv.view_mesh)
    gmsh_process.start()
    gmsh_process.join()

    game.display_switch(True)

    return True

def save_as_geo(figs : list[Figure], mode: Literal['tri', 'quad'] = "tri", game : editor.Game = None, algorithm : int = 6):
    sv = SAVER()
    sv.initialize()

    for i, fig in enumerate(figs):

        ## Ajouter les points un à un
        for pt in fig.points:
            pt = (float(pt[0] / 100), float((500 - pt[1]) / 100))
            sv.add_point(pt[0], pt[1])

        ## Ajouter les points arc un à un
        for pta in fig.points_arc:
            pta = (float(pta[0] / 100), float((500 - pta[1]) / 100))
            sv.add_point_arc(pta[0], pta[1])

        l, a = 0, 0
        ## Ajouter les lignes et les arcs dans l'ordre
        for j in range(len(fig.order)):
            if fig.order[j] == 'line':
                sv.add_line(fig.lines[l])
                l += 1
            elif fig.order[j] == 'arc':
                sv.add_arc(fig.arc[a])
                a += 1

        ## S'il reste des figures -> créer une nouvelle figure
        if i < len(figs) - 1:
            sv.add_fig()
            

    ## Créer la/les surface(s) puis finaliser
    sv.create_surface()

    ## save 
    sv.finilize()

        
    sv.save_as_geo(f"geo_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    return True


##########################################################################