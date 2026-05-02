import pygame
import math
import random
from collections import deque
from configuration import screen, largeur, hauteur

import sys

sys.setrecursionlimit(
    10000
)  # permet d'augmenter la limite de récursion de base de python


BLACK = (0, 0, 0)
PAPIER = (245, 235, 210)
OMBRE = (180, 165, 140)

# Polices et taille d'écriture
font = pygame.font.SysFont("Georgia", 15)
font_titre = pygame.font.SysFont("Georgia", 20)

Titre_x = 15
Titre_y = 15


PLAINE = 0
FORET = 1
MER = 2
SABLE = 3
MONTAGNE = 4
NEIGE = 5

noms_biomes = {
    PLAINE: "Plaine",
    FORET: "Forêt",
    MER: "Mer",
    SABLE: "Plage",
    MONTAGNE: "Montagne",
    NEIGE: "Neige",
}

palette = {
    PLAINE: (120, 200, 120),
    FORET: (20, 120, 20),
    MER: (40, 80, 200),
    SABLE: (248, 222, 126),
    MONTAGNE: (200, 210, 210),
    NEIGE: (254, 254, 226),
}

REGLES = {
    PLAINE: {PLAINE, FORET, SABLE, MONTAGNE},
    FORET: {PLAINE, FORET, MONTAGNE},
    MER: {MER, SABLE, FORET},
    SABLE: {MER, SABLE, PLAINE},
    MONTAGNE: {PLAINE, FORET, MONTAGNE, NEIGE},
    NEIGE: {MONTAGNE, NEIGE},
}

GRILLE_LARG = 38
GRILLE_HAUT = 30
TAILLE_HEX = 25
MAX_ESSAIS = 1000


def _draw_hexagon(surface, color, center, size):
    points = []
    x0, y0 = center
    for i in range(6):
        angle = math.pi / 3 * i + math.pi / 6
        points.append(
            (int(x0 + size * math.cos(angle)), int(y0 + size * math.sin(angle)))
        )
    pygame.draw.polygon(surface, color, points)


def _voisins(x, y, larg, haut):
    if y % 2 == 0:
        directions = [(-1, 0), (1, 0), (0, -1), (-1, -1), (0, 1), (-1, 1)]
    else:
        directions = [(-1, 0), (1, 0), (1, -1), (0, -1), (1, 1), (0, 1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < larg and 0 <= ny < haut:
            yield nx, ny


def _est_compatible(a, b):
    return b in REGLES[a] and a in REGLES[b]


def _copier_domaines(domaines):
    return [[cell.copy() for cell in ligne] for ligne in domaines]


def _choisir_case(domaines, larg, haut):
    meilleure_case = None
    meilleure_taille = float("inf")
    for y in range(haut):
        for x in range(larg):
            t = len(domaines[y][x])
            if 1 < t < meilleure_taille:
                meilleure_taille = t
                meilleure_case = (x, y)
    return meilleure_case


def _propager(domaines, larg, haut, depart):
    file = deque([depart])
    while file:
        x, y = file.popleft()
        domaine_case = domaines[y][x]
        for nx, ny in _voisins(x, y, larg, haut):
            ancien = domaines[ny][nx].copy()
            nouveau = {
                c for c in ancien if any(_est_compatible(cc, c) for cc in domaine_case)
            }
            if not nouveau:
                return False
            if nouveau != ancien:
                domaines[ny][nx] = nouveau
                file.append((nx, ny))
    return True


def _resoudre(domaines, larg, haut):
    case = _choisir_case(domaines, larg, haut)
    if case is None:
        return domaines
    x, y = case
    possibilites = list(domaines[y][x])
    random.shuffle(possibilites)
    for couleur in possibilites:
        tentative = _copier_domaines(domaines)
        tentative[y][x] = {couleur}
        if _propager(tentative, larg, haut, (x, y)):
            resultat = _resoudre(tentative, larg, haut)
            if resultat is not None:
                return resultat


def _generer_grille():
    couleurs = set(REGLES.keys())
    domaines = [[set(couleurs) for _ in range(GRILLE_LARG)] for _ in range(GRILLE_HAUT)]
    resultat = _resoudre(domaines, GRILLE_LARG, GRILLE_HAUT)
    if resultat is None:
        return None
    return [
        [next(iter(resultat[y][x])) for x in range(GRILLE_LARG)]
        for y in range(GRILLE_HAUT)
    ]


def _contient_tous_les_biomes(grille):
    presents = {case for ligne in grille for case in ligne}
    return set(REGLES.keys()).issubset(presents)


def _nouvelle_grille():
    derniere_valide = None
    for _ in range(MAX_ESSAIS):
        grille = _generer_grille()
        if grille is not None:
            if _contient_tous_les_biomes(grille):
                return grille
            derniere_valide = grille
    return derniere_valide


grille_onde = _nouvelle_grille()

largeur_hex = math.sqrt(3) * TAILLE_HEX
espacement_vert = 1.5 * TAILLE_HEX
CARTE_LARG = int(largeur_hex * GRILLE_LARG + largeur_hex)
CARTE_HAUT = int(espacement_vert * GRILLE_HAUT + TAILLE_HEX)

carte_onde = pygame.Surface((CARTE_LARG, CARTE_HAUT))


def dessin_onde():
    if grille_onde is None:
        return
    carte_onde.fill((0, 0, 0))
    for y in range(GRILLE_HAUT):
        for x in range(GRILLE_LARG):
            offset_x = largeur_hex / 2 if y % 2 == 1 else 0
            cx = int(x * largeur_hex + offset_x + largeur_hex / 2)
            cy = int(y * espacement_vert + TAILLE_HEX)
            couleur = palette[grille_onde[y][x]]
            _draw_hexagon(carte_onde, couleur, (cx, cy), TAILLE_HEX)
    ox = (largeur - CARTE_LARG) // 2
    oy = (hauteur - CARTE_HAUT) // 2
    screen.fill((0, 0, 0))
    screen.blit(carte_onde, (ox, oy))

    mx, my = pygame.mouse.get_pos()  # position de la souris
    couleur_pixel = screen.get_at((mx, my))[:3]
    # Code RGB du pixel

    for i in palette:
        if couleur_pixel == palette[i]:
            texte = font.render(noms_biomes[i], True, BLACK)
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

    Titre = font_titre.render("MONDE GÉNÉRÉ PAR PAQUETS D'ONDES", True, BLACK)
    largeur_titre, hauteur_titre = Titre.get_size()
    pygame.draw.rect(
        screen,
        BLACK,
        (Titre_x - 7, Titre_y - 7, largeur_titre + 16, hauteur_titre + 16),
    )
    pygame.draw.rect(
        screen,
        OMBRE,
        (Titre_x - 6, Titre_y - 6, largeur_titre + 14, hauteur_titre + 14),
    )
    pygame.draw.rect(
        screen,
        PAPIER,
        (Titre_x - 4, Titre_y - 4, largeur_titre + 10, hauteur_titre + 10),
    )
    screen.blit(Titre, (Titre_x, Titre_y))


def regenerer_wfc():
    global grille_onde
    grille_onde = _nouvelle_grille()
