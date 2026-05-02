import pygame
import random
from math import sqrt, pi, cos, sin
import heapq
from configuration import screen, largeur, hauteur, size

# -----------------------------
# Paramètres de la grille et de l'affichage
# -----------------------------
CELL_SIZE = 3  # Taille d'une case en pixels # 11 / 3
GRID_LENGTH = largeur // CELL_SIZE
GRID_HEIGHT = hauteur // CELL_SIZE  # Taille de la grille (50x50) # 60 / 250


WIDTH = GRID_LENGTH * CELL_SIZE
HEIGHT = GRID_HEIGHT * CELL_SIZE

# Couleurs (RGB)
GREEN = (34, 139, 34)  # sol
DARK_GREEN = (0, 100, 0)  # arbres
GRAY = (130, 130, 130)  # routes
BROWN = (139, 69, 19)  # maisons
BLUE = (30, 144, 255)  # fontaine
YELLOWISH = (174, 235, 63)  # cultures
YELLOWISHER = (196, 240, 53)  # variations de culture
GRAY_GREEN = (156, 179, 158)  # église
DARK_GRAY_PURPLE = (90, 110, 110)  # portes
DARK_GRAY_BROWN = (120, 90, 110)  # murailles
PAPIER = (245, 235, 210)
OMBRE = (180, 165, 140)
BLACK = (0, 0, 0)


ROUTE = 0
MAISON = 1
FONTAINE = 2
MUR = 3
BATIMENT = 4
ARBRE = 5
PLAINE = 6

noms_objets = {
    ROUTE: "Route",
    MAISON: "Maison",
    FONTAINE: "Fontaine",
    MUR: "Muraille",
    BATIMENT: "Batiment important",
    ARBRE: "Arbre",
    PLAINE: "Plaine",
}

palette = {
    ROUTE: (130, 130, 130),
    MAISON: (139, 69, 19),
    FONTAINE: (30, 144, 255),
    MUR: (120, 90, 110),
    BATIMENT: (156, 179, 158),
    ARBRE: (0, 100, 0),
    PLAINE: (34, 139, 34),
}

carte_village = pygame.Surface(size)


font_titre = pygame.font.SysFont("Georgia", 20)
font = pygame.font.SysFont("Georgia", 15)
Titre_x = 15
Titre_y = 15

# Codes des cellules
EMPTY = 0
ROAD = 1
HOUSE = 2
WELL = 3
TREE = 4
CROP = 5
CROP2 = 6
CHURCH = 7
DOOR = 8
MURAILLE = 9

grid = [[EMPTY for _ in range(GRID_HEIGHT)] for _ in range(GRID_LENGTH)]

# -----------------------------
# Paramètres des fonctions :
# -----------------------------

# place_well():

limite_bordure = (hauteur // CELL_SIZE) // 5  # 15/50
limite_bordure_hauteur = (hauteur // CELL_SIZE) // 4
limite_bordure_largeur = (largeur // CELL_SIZE) // 3

# generate_roads():

nbr_road_min = 7  # 7
nbr_road_max = 10  # 10

max_steps = 10000  # 5000

max_nearby_roads = 6  # 6

angle_naturel = 0.15  # 0.15


depth_max = 4  # 4
chance_new_branch = 0.19  # 0.19
nbr_max_branches = 55  # 55

borne_angle_new_branch = 1.0  # 1.0


# generate_houses():

# chance_house = 0.3  # 0.3
chance_house_dedans = 0.3  # 0.3
chance_house_dehors = 0.06  # 0.06

# generate_trees():

chance_tree = 0.12  # 0.12


# generate_crops():

max_crop_size = 12  # 12
min_crop_size = 7  # 7

crop_chance = 0.001  # 0.001

# Générations des cercles

facteur_adoucissant = 0.3

# Génération des murailles

épaisseur_cercle_verif_murailles = -4 / 15 * CELL_SIZE + 3.1


# -----------------------------
# Fonction : place la fontaine
# -----------------------------
def place_well():
    x = random.randint(
        limite_bordure_largeur, GRID_LENGTH - limite_bordure_largeur
    )  # position aléatoire, pas trop proche des bords
    y = random.randint(limite_bordure_hauteur, GRID_HEIGHT - limite_bordure_hauteur)
    grid[x][y] = WELL  # on marque la fontaine sur la grille
    grid[x - 1][y] = WELL
    grid[x + 1][y] = WELL
    grid[x][y - 1] = WELL
    grid[x][y + 1] = WELL
    return x, y  # on renvoie la position


# -----------------------------
# Fonction : place l'église
# -----------------------------
def place_church(x_puit, y_puit):
    cases_possibles = set(
        cases_dans_rayon(x_puit, y_puit, int(0.25 * GRID_HEIGHT))
    )  # Permet à l'église d'être placé dans un rayon autour de la fontaine
    cases_valides = {
        (x, y)
        for (x, y) in cases_possibles
        if limite_bordure_largeur <= x <= GRID_LENGTH - limite_bordure_largeur
        and limite_bordure_hauteur <= y <= GRID_HEIGHT - limite_bordure_hauteur
    }  # Permet à l'église de l'empécher d'etre placée trop près des bords

    if not cases_valides:
        cases_valides = cases_possibles  # repli de sécurité

    x, y = random.choice(list(cases_valides))

    for dx in range(-3, 2):
        for dy in range(-1, 1):
            grid[x + dx][y + dy] = CHURCH
    grid[x - 3][y - 3] = CHURCH
    grid[x - 2][y - 3] = CHURCH
    grid[x - 2][y - 2] = CHURCH
    grid[x - 1][y - 3] = CHURCH
    grid[x - 2][y - 4] = CHURCH
    grid[x][y] = DOOR  # on marque la porte
    return x, y  # on renvoie la position


# -----------------------------
# Fonction : place un batiment
# -----------------------------
def place_batiment(x_puit, y_puit, x_eglise, y_eglise):
    cases_possibles = set(
        cases_dans_rayon(x_puit, y_puit, int(0.25 * GRID_HEIGHT))
    )  # Permet au bâtiment d'être placé dans un rayon autour de la fontaine
    cases_pas_possibles = set(
        cases_dans_rayon(x_eglise, y_eglise, int(0.25 * GRID_HEIGHT))
    )  # Permet au bâtiment d'être placé en dehors d'un rayon autour de l'église
    cases_valides = (
        cases_possibles - cases_pas_possibles
    )  # cases possibles moins celles interdites
    cases_valides = {
        (x, y)
        for (x, y) in cases_possibles
        if limite_bordure_largeur <= x <= GRID_LENGTH - limite_bordure_largeur
        and limite_bordure_hauteur <= y <= GRID_HEIGHT - limite_bordure_hauteur
    }  # Permet au batiment de l'empécher d'etre placée trop près des bords

    if not cases_valides:  # aucune case disponible → on abandonne
        cases_valides = cases_possibles  # position de repli = positions avec le rayon autour de l'église possible

    x, y = random.choice(list(cases_valides))

    for dx in range(-3, 2):
        for dy in range(-1, 1):
            grid[x + dx][y + dy] = CHURCH
    grid[x - 1][y - 2] = CHURCH
    grid[x - 2][y - 2] = CHURCH
    grid[x][y - 2] = CHURCH
    grid[x][y] = DOOR  # on marque la porte
    return x, y  # on renvoie la position


# -----------------------------
# Fonction : génère les routes principales et secondaires
# -----------------------------


def generate_roads(cx, cy):
    branches = []
    # Création des routes principales (plus nombreuses pour un village dense)
    for _ in range(random.randint(nbr_road_min, nbr_road_max)):
        angle = random.uniform(0, 2 * pi)  # angle de départ aléatoire
        branches.append([cx, cy, angle, 0])  # x, y, angle, profondeur de la branche

    steps = 0
    while branches and steps < max_steps:  # on limite le nombre de pas
        branch = random.choice(branches)  # on choisit une branche au hasard
        x, y, angle, depth = branch
        ix, iy = int(x), int(y)

        # si hors grille → on supprime la branche
        if not (1 <= ix < GRID_LENGTH - 1 and 1 <= iy < GRID_HEIGHT - 1):
            branches.remove(branch)
            continue

        # calcul de la densité de routes autour pour éviter les agglomérations
        nearby_roads = sum(
            1
            for dx in range(-2, 3)
            for dy in range(-2, 3)
            if 0 <= ix + dx < GRID_LENGTH
            and 0 <= iy + dy < GRID_HEIGHT
            and grid[ix + dx][iy + dy] == ROAD
        )

        # si la zone n'est pas trop dense, on trace la route
        if nearby_roads < max_nearby_roads:
            if grid[ix][iy] in (EMPTY, ROAD):
                grid[ix][iy] = ROAD
        else:
            branches.remove(branch)
            continue

        # courbure naturelle
        angle += random.uniform(-angle_naturel, angle_naturel)

        # bifurcation : créer des rues secondaires à partir des routes principales
        if (
            depth < depth_max
            and random.random() < chance_new_branch
            and len(branches) < nbr_max_branches
        ):
            new_angle = angle + random.uniform(
                -borne_angle_new_branch, borne_angle_new_branch
            )
            branches.append([x, y, new_angle, depth + 1])

        # avancer d'une case
        x += cos(angle)
        y += sin(angle)
        branch[0] = x
        branch[1] = y
        branch[2] = angle
        branch[3] = depth
        steps += 1


# -----------------------------
# Fonction : vérifie si une maison 2x2 peut être placée
# -----------------------------
def can_place_house(x, y):
    if x < 0 or y < 0 or x + 1 >= GRID_LENGTH or y + 1 >= GRID_HEIGHT:
        return False
    # vérifie que les 4 cases sont libres
    for dx in range(2):
        for dy in range(2):
            if grid[x + dx][y + dy] != EMPTY:
                return False
    # vérifie qu'il n'y a pas d'autre maison trop proche
    for dx in range(-1, 3):
        for dy in range(-1, 3):
            nx = x + dx
            ny = y + dy
            if 0 <= nx < GRID_LENGTH and 0 <= ny < GRID_HEIGHT:
                if grid[nx][ny] == HOUSE:
                    return False
    return True


# -----------------------------
# Fonction : place une maison 2x2
# -----------------------------
def place_house(x, y):
    for dx in range(2):
        for dy in range(2):
            grid[x + dx][y + dy] = HOUSE


# -----------------------------
# Fonction : génère les maisons le long des routes
# -----------------------------
def generate_houses(zone_maisons):
    for x in range(GRID_LENGTH):
        for y in range(GRID_HEIGHT):
            if (x, y) in zone_maisons:
                chance_house = chance_house_dedans
            else:
                chance_house = chance_house_dehors
            if grid[x][y] == ROAD:
                # tester les 4 positions autour pour placer des maisons 2x2
                positions = [
                    (x - 2, y - 1),
                    (x + 1, y - 1),
                    (x - 1, y - 2),
                    (x - 1, y + 1),
                ]
                for px, py in positions:
                    if random.random() < chance_house and can_place_house(
                        px, py
                    ):  # probabilité réduite pour moins de maisons
                        place_house(px, py)


# -----------------------------
# Fonction : génère des arbres décoratifs
# -----------------------------
def generate_trees():
    for x in range(GRID_LENGTH):
        for y in range(GRID_HEIGHT):
            if (
                grid[x][y] == EMPTY and random.random() < chance_tree
            ):  # 7% des cases vides
                grid[x][y] = TREE
    return grid


# -----------------------------
# Fonction : vérifie si un champ limite_y x limite_x peut être placé
# -----------------------------


def can_place_crop(x, y, limite_x, limite_y):
    if (
        x < 0
        or y < 0
        or x + limite_x + 1 >= GRID_LENGTH
        or y + limite_y + 1 >= GRID_HEIGHT
    ):
        return False
    for dx in range(limite_x):
        for dy in range(limite_y):
            if grid[x + dx][y + dy] != EMPTY:
                return False
    return True


# -----------------------------
# Fonction : génère des champs
# -----------------------------


def generate_crops():
    for x in range(GRID_HEIGHT):
        for y in range(GRID_HEIGHT):
            limite_y = random.randint(min_crop_size, max_crop_size)
            limite_x = random.randint(min_crop_size, max_crop_size)
            if (
                can_place_crop(x, y, limite_x, limite_y)
                and random.random() < crop_chance
            ):
                for cx in range(limite_x):
                    for cy in range(limite_y):
                        if random.random() < 0.8:
                            grid[x + cx][y + cy] = CROP
                        else:
                            grid[x + cx][y + cy] = CROP2


# -----------------------------
# Fonction : génère des Cercles / Disques
# -----------------------------


def cases_dans_rayon(x, y, r):
    cases = []
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            nx, ny = x + dx, y + dy
            # Vérifie que c'est dans le cercle et dans la grille
            if (
                sqrt(dx**2 + dy**2) <= r + facteur_adoucissant
                and 0 <= nx < GRID_LENGTH
                and 0 <= ny < GRID_HEIGHT
            ):
                cases.append((nx, ny))
    return cases


# cercle creux
# PS : Cette fonction ne sert pas à part si on décide de changer la génération des murailles avce l'autre fonction pour
def cases_du_rayon(x, y, r):
    cases = []
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            nx, ny = x + dx, y + dy
            # Vérifie que c'est dans le cercle et dans la grille
            if (
                sqrt(dx**2 + dy**2) <= r + facteur_adoucissant
                and sqrt(dx**2 + dy**2) > r - (1 + facteur_adoucissant)
                and 0 <= nx < GRID_LENGTH
                and 0 <= ny < GRID_HEIGHT
            ):  # (r + facteur_adoucissant) - (1 + 0.1 * facteur_adoucissant)
                cases.append((nx, ny))
    return cases


# -----------------------------
# Fonction : Génère les murailles
# -----------------------------


# ATTENTION, CETTE METHODE MARCHE TRES BIEN MAIS NE PREND PAS EN COMPTE LE CAS TRES RARE OU LES TROIS CERCLES SE RENCONTRENT EN 1 POINT, MAIS PEUT ÊTRE UNE GENERATION + NATURELLE
# def generate_murailles_et_zone_maisons(cx_puit, cy_puit, cx_eglise, cy_eglise, cx_batiment, cy_batiment):
#     disque_puit = set(cases_dans_rayon(cx_puit, cy_puit, int(0.25 * GRID_HEIGHT)))
#     disque_eglise = set(cases_dans_rayon(cx_eglise, cy_eglise, int(0.25 * GRID_HEIGHT)))
#     disque_batiment = set(cases_dans_rayon(cx_batiment, cy_batiment, int(0.25 * GRID_HEIGHT)))
#     cercle_puit = set(cases_du_rayon(cx_puit, cy_puit, int(0.25 * GRID_HEIGHT)))
#     cercle_eglise = set(cases_du_rayon(cx_eglise, cy_eglise, int(0.25 * GRID_HEIGHT)))
#     cercle_batiment = set(cases_du_rayon(cx_batiment, cy_batiment, int(0.25 * GRID_HEIGHT)))
#     murailles = (cercle_puit - disque_batiment - disque_eglise) | (cercle_eglise - disque_puit - disque_batiment) | (cercle_batiment - disque_puit - disque_eglise)
#     for case in cercle_puit:
#         if case not in disque_batiment:
#             murailles = murailles | (set([case]) & cercle_eglise)
#     for case in cercle_puit:
#         if case not in disque_eglise:
#             murailles = murailles | (set([case]) & cercle_batiment)
#     for case in cercle_batiment:
#         if case not in disque_puit:
#             murailles = murailles | (set([case]) & cercle_eglise)
#     # (cercle_puit & cercle_eglise) | (cercle_puit & cercle_batiment) | (cercle_eglise & cercle_batiment)
#     for (x, y) in murailles:
#         grid[x][y] = MURAILLE
#     return disque_puit | disque_eglise | disque_batiment


# MEME FONCTION QUE PLUS HAUT MAIS QUI VERIFIE EN CERCLES (plus jolie et adapté)
def generate_murailles_et_zone_maisons(
    cx_puit,
    cy_puit,
    cx_eglise,
    cy_eglise,
    cx_batiment,
    cy_batiment,
    epaisseur=épaisseur_cercle_verif_murailles,
):
    disque_puit = set(cases_dans_rayon(cx_puit, cy_puit, int(0.25 * GRID_HEIGHT)))
    disque_eglise = set(cases_dans_rayon(cx_eglise, cy_eglise, int(0.25 * GRID_HEIGHT)))
    disque_batiment = set(
        cases_dans_rayon(cx_batiment, cy_batiment, int(0.25 * GRID_HEIGHT))
    )

    union = disque_puit | disque_eglise | disque_batiment
    e = int(epaisseur) + 1  # rayon du carré à explorer

    murailles = set()
    for x, y in union:
        for dx in range(-e, e + 1):
            for dy in range(-e, e + 1):
                # on vérifie dans un cercle de rayon epaisseur (et non un carré)
                if sqrt(dx**2 + dy**2) <= epaisseur:
                    nx, ny = x + dx, y + dy
                    # on ignore les voisins hors de la grille
                    if 0 <= nx < GRID_LENGTH and 0 <= ny < GRID_HEIGHT:
                        if (nx, ny) not in union:
                            murailles.add((x, y))
                            break
            else:
                continue
            break

    for x, y in murailles:
        grid[x][y] = MURAILLE
    return union


# -----------------------------
# Fonction : génère tout le village
# -----------------------------


def generate_village():
    cx_puit, cy_puit = place_well()  # place la fontaine
    cx_eglise, cy_eglise = place_church(cx_puit, cy_puit)  # place l'église
    cx_batiment, cy_batiment = place_batiment(cx_puit, cy_puit, cx_eglise, cy_eglise)
    # remplace_chemin_plus_court(grid, (cx_puit, cy_puit), (cx_eglise, cy_eglise))
    # remplace_chemin_plus_court(grid, (cx_puit, cy_puit), (cx_batiment, cy_batiment))
    generate_roads(cx_puit, cy_puit)  # routes principales et secondaires
    generate_roads(cx_eglise, cy_eglise)  # routes principales et secondaires
    generate_roads(cx_batiment, cy_batiment)  # routes principales et secondaires
    zone_maisons = generate_murailles_et_zone_maisons(
        cx_puit, cy_puit, cx_eglise, cy_eglise, cx_batiment, cy_batiment
    )
    generate_houses(zone_maisons)  # maisons le long des routes
    # generate_crops()  # Champs de culture
    generate_trees()  # arbres décoratifs
    return grid


# -----------------------------
# Fonction : dessin à l'écran
# -----------------------------
def dessin_village():
    for x in range(GRID_LENGTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if grid[x][y] == EMPTY:
                pygame.draw.rect(carte_village, GREEN, rect)
            elif grid[x][y] == ROAD:
                pygame.draw.rect(carte_village, GRAY, rect)
            elif grid[x][y] == HOUSE:
                pygame.draw.rect(carte_village, BROWN, rect)
            elif grid[x][y] == WELL:
                pygame.draw.rect(carte_village, BLUE, rect)
            elif grid[x][y] == TREE:
                pygame.draw.rect(carte_village, DARK_GREEN, rect)
            elif grid[x][y] == CHURCH:
                pygame.draw.rect(carte_village, GRAY_GREEN, rect)
            elif grid[x][y] == DOOR:
                pygame.draw.rect(carte_village, DARK_GRAY_PURPLE, rect)
            elif grid[x][y] == MURAILLE:
                pygame.draw.rect(carte_village, DARK_GRAY_BROWN, rect)
            elif grid[x][y] == CROP:
                pygame.draw.rect(carte_village, YELLOWISH, rect)
            elif grid[x][y] == CROP2:
                pygame.draw.rect(carte_village, YELLOWISHER, rect)

    screen.fill(BLACK)
    screen.blit(
        carte_village, (0, 0)
    )  # ((largeur - WIDTH) // 2, (hauteur - HEIGHT) // 2))

    Titre = font_titre.render("Un super village", True, BLACK)
    largeur_titre, hauteur_titre = Titre.get_size()
    pygame.draw.rect(
        carte_village,
        BLACK,
        (Titre_x - 7, Titre_y - 7, largeur_titre + 16, hauteur_titre + 16),
    )
    pygame.draw.rect(
        carte_village,
        OMBRE,
        (Titre_x - 6, Titre_y - 6, largeur_titre + 14, hauteur_titre + 14),
    )
    pygame.draw.rect(
        carte_village,
        PAPIER,
        (Titre_x - 4, Titre_y - 4, largeur_titre + 10, hauteur_titre + 10),
    )
    carte_village.blit(Titre, (Titre_x, Titre_y))

    mx, my = pygame.mouse.get_pos()  # position de la souris
    couleur_pixel = screen.get_at((mx, my))[:3]
    # Code RGB du pixel

    for i in palette:
        if couleur_pixel == palette[i]:
            texte = font.render(noms_objets[i], True, BLACK)
            largeur_texte, hauteur_texte = texte.get_size()
            pygame.draw.rect(
                screen,
                BLACK,
                (mx + 12, my + 12, largeur_texte + 16, hauteur_texte + 16),
            )
            pygame.draw.rect(
                screen,
                OMBRE,
                (mx + 13, my + 13, largeur_texte + 14, hauteur_texte + 14),
            )
            pygame.draw.rect(
                screen,
                PAPIER,
                (mx + 15, my + 15, largeur_texte + 10, hauteur_texte + 10),
            )
            screen.blit(texte, (mx + 20, my + 20))


# generate_village()

# -----------------------------
# Fonction : Régénérer le village
# -----------------------------


def regenerer_village():
    grid[:] = [[EMPTY for _ in range(GRID_HEIGHT)] for _ in range(GRID_LENGTH)]
    return grid


# ------------------------------------------------------------------------------------------------------------------------------
# Algorithme A* :


def cheminPlusCourt(grille, depart, objectif):
    """
    A* sur la grille. depart et objectif sont des tuples (x, y).
    Retourne une liste de tuples (x, y) formant le chemin, ou [] si aucun chemin.
    """

    def heuristique(a, b):
        return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    open_list = []
    compteur = 0
    heapq.heappush(open_list, (0, compteur, depart))

    parent = {}  # (x,y) -> (x,y) parent
    cout_g = {}  # coût réel depuis le départ
    cout_g[depart] = 0

    while open_list:
        _, _, u = heapq.heappop(open_list)

        if u == objectif:
            # Reconstituer le chemin
            chemin = []
            while u in parent:
                chemin.append(u)
                u = parent[u]
            chemin.pop(0)
            # chemin.pop(1)
            chemin.reverse()
            chemin.pop(0)
            return chemin

        x, y = u
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < GRID_LENGTH and 0 <= ny < GRID_HEIGHT):
                continue
            # On ne traverse que les cases vides ou déjà routes
            if (
                grille[nx][ny] != EMPTY
                and grille[nx][ny] != ROAD
                and grille[nx][ny] != WELL
                and grille[nx][ny] != DOOR
                and grille[nx][ny] != CHURCH
            ):
                continue

            v = (nx, ny)
            nouveau_cout = cout_g[u] + 1

            if v not in cout_g or nouveau_cout < cout_g[v]:
                cout_g[v] = nouveau_cout
                priorite = nouveau_cout + heuristique(v, objectif)
                compteur += 1
                heapq.heappush(open_list, (priorite, compteur, v))
                parent[v] = u
    print("Pas de chemin")
    return []  # Aucun chemin trouvé


def remplace_chemin_plus_court(grille, depart, objectif):
    chemin = cheminPlusCourt(grille, depart, objectif)
    for x, y in chemin:
        grille[x][y] = ROAD
    return grille
