import re

from geometry.figure    import Figure
from geometry.arc       import Arc
from geometry.line      import Line
from geometry.point     import Point

class Reader:
    def __init__(self):
        pass

    def read(self, path: str) -> list[Figure]:
        pattern = re.compile(r"(\w+)\((\d+)\) = \{([^}]+)\};")
        results = {}

        pts : list[Point]     = []
        forms   = []

        with open(path, "r") as f:
            for match in pattern.finditer(f.read()):
                mot_clef, indice, valeurs = match.groups()
                indice = int(indice)
                valeurs = [v.strip() for v in valeurs.split(",")]

                if mot_clef not in results: results[mot_clef] = {}
                results[mot_clef][indice] = valeurs

        for mot_clef, data in results.items():
            if mot_clef == "Point":
                for indice, valeurs in data.items():
                    pts.append(Point(float(valeurs[0]) *100, 500 - float(valeurs[1]) * 100, indice - 1))

            elif mot_clef == "Line":
                for indice, valeurs in data.items():
                    forms.append(Line(pts[int(valeurs[0]) - 1], pts[int(valeurs[1]) - 1], indice - 1))

            elif mot_clef == "Circle":
                for indice, valeurs in data.items():
                    forms.append(Arc(pts[int(valeurs[0]) - 1], pts[int(valeurs[2]) - 1], pts[int(valeurs[1]) - 1], indice - 1))
                    pts[int(valeurs[1]) - 1].is_arc_point = True

        figures : list[Figure] = []


        min = 999999999.0
        index = -1

        while len(forms) > 0:
            fig_points = []
            fig_forms  = []

            # On cherche la forme avec l'ID la plus petite
            for i, f in enumerate(forms):
                if f.id < min:
                    min = f.id
                    index = i
            
            # Une fois trouvé, poursuit les autres points jusqu'à retrouver le point de départ
        
            frm = forms[index]
            forms.pop(index)

            starting_point = frm.p1

            if isinstance(frm, Line):
                fig_forms.append(frm)
                fig_points.append(frm.p1)
            elif isinstance(frm, Arc):
                fig_forms.append(frm)
                fig_points.append(frm.p1)
                fig_points.append(frm.pc)
            
            while frm.p2 != starting_point:
                for f in forms:
                    if f.p1 != frm.p2:
                        continue 

                    frm = f
                    forms.remove(f)

                    if isinstance(frm, Line):
                        fig_forms.append(frm)
                        fig_points.append(frm.p1)
                    elif isinstance(frm, Arc):
                        fig_forms.append(frm)
                        fig_points.append(frm.p1)
                        fig_points.append(frm.pc)
                    break
            
            # print(fig_forms)

            fig_forms.pop(-1) # Retire la dernière ligne (gérée automatiquement par l'éditeur)

            fig = Figure()
            fig.points = fig_points
            fig.forms  = fig_forms

            fig.remake_ids()

            figures.append(fig)
            min = 999999999
        return figures
        

if __name__ == "__main__":
    rd = Reader()

    figs : list[Figure] = rd.read("T2.geo_unrolled")

    for f in figs:
        print(f.forms)

    