import gmsh
import math

from datetime import datetime
from typing import Literal

class GMSH_CREATOR:
    def __init__(self):
        self.points  = []
        self.lines   = []
        self.surface = None

    def initialize(self):
        gmsh.initialize()
        gmsh.clear()
        gmsh.model.add("form")

    def add_point(self, x, y):
        self.points.append(gmsh.model.geo.add_point(x, y, 0))

    def finilize(self):
        ## Créer les lignes
        for i in range(len(self.points) - 1):
            self.lines.append(gmsh.model.geo.addLine(self.points[i], self.points[i + 1]))
        
        self.lines.append(gmsh.model.geo.addLine(self.points[-1], self.points[0]))

        ## Créer la surface
        loop = gmsh.model.geo.add_curve_loop(self.lines)
        surface = gmsh.model.geo.add_plane_surface([loop])

        ## Créer le maillage
        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(2)
        

    def view_mesh(self):
        gmsh.fltk.run()

    def save(self, filename):
        gmsh.write(filename+'.msh')

##########################################################################

def automatize(points, mode: Literal['tri', 'quad'] = "tri"):
    gc = GMSH_CREATOR()
    gc.initialize()

    for p in points:
        p = (float(p[0]/100), float((500 - p[1])/100))
        gc.add_point(p[0], p[1])
    
    gc.finilize()
    gc.create_surface()
    gc.create_mesh()

    gc.save(f'mesh_tri_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.msh')


##########################################################################
