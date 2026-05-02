import random as rand
from copy import deepcopy
from collections import defaultdict
import heapq
import math


"""A LIRE SI VOUS NE COMPRENEZ LA SPLINE DE CATMULL-ROM (en espérant que ca aide !) les points du début et de la fin servent
seulement à calculer la spline (donc des "ghosts points")

Dans les tangentes, le /2 est optionnel, on pourrait très bien l'enlever pour avoir une courbure plus marquée.

La tangente au point P1 est le vecteur (P2-P0) :
on fait comme si P0 faisait partie de la courbe et on regarde la direction de P0 à P2
(P2 - P0)/2 est la tangente en P1 elle sert à savoir vers où partir.

On fait similairement de P3 à P1. Ainsi, (P3 - P1)/2 est la tangente en P2.

Elle nous sert à savoir comment arriver en P2. tang_1 et tang_2 définissent donc le chemin vers la courbe
en un point P de la courbe, la tangente correspond à la dérivée de la formule, elle dépend donc de tang_1, tang_2 et les coordonnées des points considérés.

On trace la courbe en calculant plein de points pour différentes valeurs de t et en les reliant entre eux.
(Sur la formule) Comment on sait que l'on va atteindre P2 ? La formule est sensée donner pour t = 1 exactement P2 (et P1 pour t= 0)

La formule une courbe d'Hermite, f(t) = h1 + h2 * t + h3 * t^2 + h4 * t^3 construite afin de forcer les propriétés de CM:
h1 = P1 (P(0) = P1 grâce à h1)
(h2 * t)' = tang_1 (donc tangente en P1 = P'0 = h2(t) = tang_1 = (P2 - P0)/2)
On peut aussi vérifier que P'(1) = tang_2
h3 et h4 sert à contrôler l'influence des tangentes sur la courbe de manière à ce que : tang_1 (début) perde de l'influence et tang_2 (fin) en gagne au fur et à mesure que t augmente.
Comment ? La tang_2 se trouve dans h3 et h4 qui sont les termes en t^2 qui deviendront de plus en plus importants au fur et à mesure que t se rapproche de 1."""


def Catmull_Rom(P0, P1, P2, P3, t):
    x_P3 = P3[0]  # P3
    y_P3 = P3[1]
    x_P1 = P1[0]  # P1
    y_P1 = P1[1]
    x_P2 = P2[0]  # P2
    y_P2 = P2[1]
    x_P0 = P0[0]  # P0
    y_P0 = P0[1]
    tang_1 = (x_P2 - x_P0) / 2
    tang_1_y = (y_P2 - y_P0) / 2
    tang_2 = (x_P3 - x_P1) / 2
    tang_2_y = (y_P3 - y_P1) / 2
    pt_x = (
        x_P1 + (tang_1) * t + ((-3) * x_P1 - 2 * (tang_1) - tang_2 + 3 * (x_P2)) * (t**2) + (2 * (x_P1) + tang_1 + tang_2 - 2 * (x_P2)) * (t**3)
    )
    pt_y = (
        y_P1 + (tang_1_y) * t + ((-3) * y_P1 - 2 * (tang_1_y) - tang_2_y + 3 * (y_P2)) * (t**2) + (2 * (y_P1) + tang_1_y + tang_2_y - 2 * (y_P2)) * (t**3)
    )
    return (pt_x, pt_y)


# Les frontières : On va attribuer une valeur aléatoire qui va petit à petit être réduite au fur et à mesures qu'on ajoute des cases dans une direction aléatoire
# Entrée : Map : matrice et n nombre de biomes que l'on veut créer


directions = [[-1, -1], [-1, 0], [0, -1], [0, 1], [1, 0], [1, 1], [1, -1], [-1, 1]]


def frontières_V2(Map, n):
    min_v = 700
    max_v = 2000
    tranche_min = 50
    tranche_max = 70
    cases_vides = set()  # Un set, c'est un objet qui prend de manière aléatoire tous les élements d'une liste et supprime
    # les doublons. C'est très pratique de l'avoir car il possède aussi une méthode discard qui ne plante pas si l'objet
    # n'est pas dans la liste. Gardez cette information en tête c'est important plus tard.
    for i in range(len(Map)):
        for j in range(len(Map[i])):
            cases_vides.add((i, j))
    for t in range(1, n + 1):
        x = rand.randrange(0, len(Map))
        y = rand.randrange(0, len(Map))
        Map[x][y] = t
        cases_vides.discard((x, y))
        v = rand.randrange(min_v, max_v)
        while v > 0:
            b = any(
                ((x + directions[i][0]) % len(Map), (y + directions[i][1]) % len(Map))
                in cases_vides
                for i in range(len(directions))
            )
            if not b:
                break
            direction = rand.randrange(len(directions))
            d_x = (x + directions[direction][0]) % len(Map)
            d_y = (y + directions[direction][1]) % len(Map)
            if ((d_x, d_y) in cases_vides) is True:
                Map[d_x][d_y] = t
                x = d_x
                y = d_y
                cases_vides.discard((d_x, d_y))
                v = v - rand.randrange(tranche_min, tranche_max)
            else:
                pass
    return Map

# On entre dans le Marching squares. On commence par définir une fonction d'interpolation car on va avoir besoin d'information
# sur les courbes plus tard. Une interpolation c'est une approximation (locale) d'une courbe, c'est un peu (je dis bien un peu)
# comme les DL en analyse.


def interpolate(p1, p2, v1, v2, seuil):
    if v1 == v2:
        return p1
    t = (seuil - v1) / (v2 - v1)
    return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))


# Fonction pour reconstruire la forme à partir des segments qu'on va récupérer nous, on parcourt avant puis arrière et
# on relie les deux à la moitié, on utilise pour ca un graphe afin de pouvoir suivre l'ordre des segments au lieu de
# les relier au hasard...


def build_polylines(segments):
    graph = defaultdict(list)
    for a, b in segments:
        graph[a].append(b)
        graph[b].append(a)

    polylines = []
    used_edges = set()  # On tient un dico de chemins/arêtes déjà visité(e)s, pour que quand l'arrière essaie d'utiliser
    # une arête qui à déjà été utilisée par l'avant le programme le stoppe.
    # Une autre utilité non négligeable : ça permet d'éviter de revenir sur ses pas...
    # On utilise encore un set pour éviter tout ce qui est doublons (et parce qu'on va passer notre temps à retirer des objets)
    # La boucle ci-dessous commence la reconstruction des formes.
    for start_a, start_b in segments:
        # Initialisation
        if (start_a, start_b) in used_edges or (start_b, start_a) in used_edges:
            continue

        poly = [start_a, start_b]
        used_edges.add((start_a, start_b))

        # avancer vers l'avant (1er sens...)
        # Ici on essaie de trouver une arête à traverser, donc on prend notre point courant
        # et on essaie de trouver un point parmi ses voisns dont on a pas utilisé l'arête ce qui se traduit dans le code ci-dessous :
        prev, current = start_a, start_b  # ca veut dire prev = start_a et current = start_b ce n'est pas décidé au hasard
        while True:  # Ca ne devrait pas poser problème, le but c'est de break cette boucle...
            next_pt = None
            for n in graph[current]:
                if n != prev and (current, n) not in used_edges and (n, current) not in used_edges:
                    next_pt = n
                    break  # Ce break casse le for i in range, pas le while, parce que il faut remplacer le point courant
                    # une fois qu'on a trouvé un point auquel se déplacer.

            if next_pt is None:
                break  # ...Ici, quand on ne trouve pas d'autre point.

            poly.append(next_pt)
            used_edges.add((current, next_pt))
            prev, current = current, next_pt

        # avancer vers l'arrière (...2ème sens), on fait la même chose.
        prev, current = start_b, start_a
        while True:
            next_pt = None
            for n in graph[current]:
                if n != prev and (current, n) not in used_edges and (n, current) not in used_edges:
                    next_pt = n
                    break

            if next_pt is None:
                break

            poly.insert(0, next_pt)
            used_edges.add((current, next_pt))
            prev, current = current, next_pt

        polylines.append(poly)

    return polylines

# Snap : pour arrondir les float qui sont pas calculés parfaitement (ex : (1,0002, 2) != (1, 2) et ca casse tout !)


def snap(p, precision=1):
    return (round(p[0], precision), round(p[1], precision))

# Pour pouvoir détecter les frontières bien proprement, on utilise un SDF (non c'est pas un sans-abri, c'est un Signed
# Distance Field). Le but c'est d'(1)initalement mettre 0 aux points qui se trouvent au plus proche de la frontière,
# qui elle est entre les points (0 | 0)
# (2) puis de créer une propagation de la distance au bord. A chaque point on assigne la distance la plus proche du bord
# par exemple on a (1 0 | 0 1)
# Ca créée un gradian (comme pour Ep en méca) qui nous guide vers les autres points (l'ia m'a parlé de "champ continu"
# mais je suis pas sûr d'avoir compris ca...)
# (3) Pour différencier les points intérieurs des points extérieurs, on utilise une convention de signe (négatif en dehors
# positif sinon) d'où le "Signed" (donc notre exemple de tout à l'heure devient (-1 0 | 1 0) si le biome est à droite)
# (4) à la fin on ajoute 0.5 (ou -0.5) aux points qui avaient 0 car notre MS va chercher un changement de signe pour détecter
# la frontière. Si on a que des 0 ca risque de l'aveugler et donc de ne rien détecter du tout.


def distance_field(Map, n):
    h, w = len(Map), len(Map[0])
    dist = [[math.inf] * w for _ in range(h)]
    heap = []

    directions = [
        (-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1),
        (-1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)),
        (1, -1, math.sqrt(2)), (1, 1, math.sqrt(2))
    ]
    # les sqrt(2) c'est pour les directions en diagonale, qui nous donnent une propagation circulaire
    # initialisation frontière
    # (1)
    for i in range(h):
        for j in range(w):
            for di, dj, _ in directions[:4]:
                ni, nj = i + di, j + dj
                if 0 <= ni < h and 0 <= nj < w:

                    if Map[i][j] != Map[ni][nj]:
                        # frontière entre (i,j) et (ni,nj)

                        dist[i][j] = 0
                        dist[ni][nj] = 0

                        heapq.heappush(heap, (0, i, j))
                        heapq.heappush(heap, (0, ni, nj))

    # (2) On trouve la distance entre les points de la map et la figure
    while heap:
        d, i, j = heapq.heappop(heap)

        if d > dist[i][j]:
            continue

        for di, dj, cost in directions:
            ni = (i + di)
            nj = (j + dj)
            if 0 <= ni < len(Map) and 0 <= nj < len(Map[0]):

                nd = d + cost

                if nd < dist[ni][nj]:
                    dist[ni][nj] = nd
                    heapq.heappush(heap, (nd, ni, nj))

    # (3) Le signe : étant donné que plus tard on fait une étude de signe pour déterminer si la courbe passe par là
    # ou non, il est primoridal de poser une règle avec un signe. Convention : positif si dans le biome, négatif sinon.
    for i in range(h):
        for j in range(w):
            if Map[i][j] != n:
                dist[i][j] = -dist[i][j] - 0.5  # (4)
            else:
                dist[i][j] = dist[i][j] + 0.5  # (4)

    return dist

# Le morceau principal. Ici, on relie toutes les étapes :
# D'abord on utilise notre SDF pour détecter les frontières...


def Marching_squares(Map, n, SEUIL=0):
    MAP = deepcopy(Map)
    h = len(MAP)
    w = len(MAP[0])
    segments = []
    MAP = distance_field(MAP, n)  # ... juste ici.

    # On va maintenant chercher ou exactement notre courbe (qui représente la frontière) coupe nos cellules...

    for j in range(h - 1):
        for i in range(w - 1):
            # Définition de la cellule, ici les distances...
            v0 = MAP[j][i]
            v1 = MAP[j][i + 1]
            v2 = MAP[j + 1][i]
            v3 = MAP[j + 1][i + 1]

            # ...et ici les coordonnées des coins
            tl = (i, j)
            tr = (i + 1, j)
            bl = (i, j + 1)
            br = (i + 1, j + 1)

            edges = {}

            # Les côtés du carré

            # HAUT
            if (v0 - SEUIL) * (v1 - SEUIL) < 0:
                edges["top"] = snap(interpolate(tl, tr, v0, v1, SEUIL))

            # DROITE
            if (v1 - SEUIL) * (v3 - SEUIL) < 0:
                edges["right"] = snap(interpolate(tr, br, v1, v3, SEUIL))

            # BAS
            if (v2 - SEUIL) * (v3 - SEUIL) < 0:
                edges["bottom"] = snap(interpolate(bl, br, v2, v3, SEUIL))

            # GAUCHE
            if (v0 - SEUIL) * (v2 - SEUIL) < 0:
                edges["left"] = snap(interpolate(tl, bl, v0, v2, SEUIL))

            # --- connexions (relier les points), c'est ici la table. --- #
            # Il a fallu hardcoder les deux cas où l'ordre d'ajout nous embête, sinon on prend le risque de l'aléatoire
            # Ce n'est pas forcément nécessaire mais c'est une sécurité car on travaille en float et les float ca peut parfois
            # faire partir légèrement en sucette (1,0001 au lieu de 1 par exemple.)
            if len(edges) == 2:
                if "top" in edges and "bottom" in edges:
                    segments.append((edges["top"], edges["bottom"]))
                elif "left" in edges and "right" in edges:
                    segments.append((edges["left"], edges["right"]))
                else:
                    pts = list(edges.values())
                    segments.append((pts[0], pts[1]))
            # Ici les cas ambigus (et affreux) où deux segments sont tracés. Il y a deux possibilités d'interpréter ces cas
            # et pas moyen facile de trancher quelle configuration adopter, il faut donc trouver un moyen de décider.
            # dans ce programme, je calcule la fonction au centre f(0,5;0,5) et si c'est positif, alors la plupart de la
            # cellule sera positive donc on prend une configuration. Sinon, on prend une autre configuration. En réalité, si
            # on trace la courbe exacte (si vous voulez savoir la fonction est une fonction qui utilise deux paramètres
            # libres x et y compris entre 0 et 1, et quatre paramètres fixes qui sont f(0,0) = v0 f(1,0) = v1 f(0,1) = v2 f(1,1) = v3),
            # alors la fonction devrait naturellement prendre une courbe ressemblant à une configuration.
            elif len(edges) == 4:
                center = (v0 + v1 + v2 + v3) / 4

                if center > SEUIL:
                    segments.append((edges["top"], edges["right"]))
                    segments.append((edges["bottom"], edges["left"]))
                else:
                    segments.append((edges["top"], edges["left"]))
                    segments.append((edges["bottom"], edges["right"]))
    # print("segments:", len(segments)) (c'était un test)
    return build_polylines(segments)  # enfin ici on reconstruit la figure.
