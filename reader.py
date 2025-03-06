import re

def read(path : str) -> list:
    pattern = re.compile(r"(\w+)\((\d+)\) = \{([^}]+)\};")
    results = {}

    all_pts  = []
    pts      = []
    pts_arc  = []
    lines    = []
    arcs     = []
    arcs_idx = []

    ### On récupère tous les points, lignes et arc de cercles
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
                all_pts.append( (float(valeurs[0]) * 100, 500 - float(valeurs[1]) * 100))
        
        elif mot_clef == "Line":
            for indice, valeurs in data.items():
                lines.append((int(valeurs[0]) - 1, int(valeurs[1]) - 1))

        elif mot_clef == "Circle":
            for indice, valeurs in data.items():
                arcs.append((int(valeurs[0]) - 1, int(valeurs[2]) - 1, int(valeurs[1]) - 1))
                arcs_idx.append(int(valeurs[1]) - 1)

    for i, pt in enumerate(all_pts):
        if i in arcs_idx:
            pts_arc.append(pt)
        else:
            pts.append(pt)
        
    # print("Points:", pts)
    # print("Points Arc:", pts_arc)
    # print("Lines:", lines)
    # print("Arcs:", arcs)

    ### On recréer les figures afin de pouvoir les implémenter correctement.
    
    forms = lines + arcs

    min = 999999999
    id  = -1

    form = []

    while len(forms) > 0:
        ln  = []
        ac  = []
        pt  = []
        pta = []
        ord = []

        # On cherche parmi toutes les formes, celui qui a le point [0] avec l'ID le plus petit.
        for i, f in enumerate(forms):
            if f[0] < min:
                min = f[0]
                id  = i

        # Une fois qu'on l'a trouvé, on poursuit les autres points jusqu'à retrouver le point de départ.
        
        frm = forms[id]
        forms.pop(id)

        pt.append(all_pts[frm[0]])
        if      len(frm) == 2:
            ln.append(frm)
            ord.append("line")
        elif    len(frm) == 3: 
            ac.append(frm)
            ord.append("arc")
            pta.append(all_pts[frm[2]])

        while frm[1] != min:
            for f in forms:
                if f[0] == frm[1]:
                    frm = f
                    forms.remove(f)
                    pt.append(all_pts[frm[0]])
                    if      len(frm) == 2:
                        ln.append(frm)
                        ord.append("line")
                    elif    len(frm) == 3: 
                        ac.append(frm)
                        ord.append("arc")
                        pta.append(all_pts[frm[2]])
                    break
        ln.pop(-1)
        ord.pop(-1)

        # On reformule les index des lignes/arcs parce que sinon --> o amaldiçoado index out of range

        ida = 0

        for i in range(len(pt)):
            pt[i] = (int(pt[i][0]), int(pt[i][1]))

        for i in range(len(ln)):
            ln[i] = (ln[i][0] - min, ln[i][1] - min)
        
        for i in range(len(ac)):
            ac[i] = ((ac[i][0] - min, ac[i][1] - min), ida)
            ida += 1

        form.append((pt, ln, ac, pta, ord))
        min = 999999999

    return form

if __name__ == "__main__":
    figs = read("TEST.geo_unrolled")