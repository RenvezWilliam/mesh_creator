import multiprocessing.process
import gmsh
from datetime import datetime

from geometry.figure import Figure
from geometry.arc import Arc
from geometry.line import Line

import multiprocessing

class Saver:
    def __init__(self):
        self.points = []
        self.forms  = []
        self.f_id   = 0

        self.points.append([])
        self.forms.append([])
    
    def _add_fig(self):
        self.points.append([])
        self.forms.append([])
        self.f_id += 1

    def _initialize(self):
        self.f_id = 0
        gmsh.initialize()
        gmsh.option.set_number("General.Terminal", 0)
        gmsh.clear()
        gmsh.model.add("form")
    
    def _add_point(self, x, y):
        self.points[self.f_id].append(gmsh.model.geo.add_point(x, y, 0, 1))

    def _add_line(self, p1, p2):
        self.forms[self.f_id].append(gmsh.model.geo.add_line(self.points[self.f_id][p1], self.points[self.f_id][p2]))
        
    def _add_circle(self, p1, p2, pc):
        self.forms[self.f_id].append(gmsh.model.geo.add_circle_arc(self.points[self.f_id][p1], self.points[self.f_id][pc], self.points[self.f_id][p2]))
    
    def _create_surface(self):
        loops = []

        for i in range(self.f_id + 1):
            # Ajout de la dernière ligne
            last_valid_point = [p for p in self.figs[i].points if not p.is_arc_point][-1]
            id_obj = self.figs[i].points.index(last_valid_point)

            self.forms[i].append(gmsh.model.geo.add_line(self.points[i][id_obj], self.points[i][0]))

            loops.append(gmsh.model.geo.add_curve_loop(self.forms[i]))
        
        gmsh.model.geo.add_plane_surface(loops)
    
    def _finilize(self, is_subdivized : bool = False, algorithm : int = 6):
        if is_subdivized:
            gmsh.option.set_number("Mesh.SubdivisionAlgorithm", 1)
        else:
            gmsh.option.set_number("Mesh.SubdivisionAlgorithm", 0)
        
        gmsh.option.set_number("Mesh.Algorithm", algorithm)

        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(1)
        gmsh.model.mesh.generate(2)

    def _view_mesh(self):
        gmsh.fltk.run()

    def _save_mesh(self, filename):
        gmsh.write(filename+'.msh')
    
    def _save_geo(self, filename):
        gmsh.write(filename+".geo_unrolled")

    def _create_geometry(self, figs : list[Figure], is_subdivised = False, algorithm: int = 6):
        self._initialize()

        self.figs = figs

        for i, fig in enumerate(figs):
            # Ajout des points
            for p in fig.points:
                pt = (float(p.x / 100), float((500 - p.y) / 100))
                self._add_point(pt[0], pt[1])

            # Ajout des formes (en utilisant l'id des points)
            for f in fig.forms:
                if isinstance(f, Line):
                    p1 = fig.points.index(f.p1)
                    p2 = fig.points.index(f.p2)
                    self._add_line(p1, p2)
                if isinstance(f, Arc):
                    p1 = fig.points.index(f.p1)
                    p2 = fig.points.index(f.p2)
                    pc = fig.points.index(f.pc)
                    self._add_circle(p1, p2, pc)

            if i < len(figs) - 1 : self._add_fig()
        
        self._create_surface()

        self._finilize(is_subdivised, algorithm)


    def save_mesh(self, figs : list[Figure], is_subdivised = False, algorithm: int = 6):
        self._create_geometry(figs, is_subdivised, algorithm)

        if is_subdivised:
            self._save_mesh(f"mesh_subdivised_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        else:
            self._save_mesh(f"mesh_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        
        return True
    
    def save_geo(self, figs : list[Figure]):
        self._create_geometry(figs)

        self._save_geo(f"geo_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        
        return True
    
    def view(self, figs: list[Figure], game = None, is_subdivised = False, algorithm: int = 6):
        if game == None: return

        self._create_geometry(figs, is_subdivised, algorithm)

        game.display_switch(False)

        gmsh_process = multiprocessing.Process(target=self._view_mesh())
        gmsh_process.start()
        gmsh_process.join()

        game.display_switch(True)

        return True
