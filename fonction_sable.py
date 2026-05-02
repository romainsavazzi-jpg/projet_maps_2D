import pygame
import math
import random
from configuration import screen, size, largeur, hauteur

pygame.init()
running = True

# Couleurs et cases

# COULEURS

BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (200, 255, 0)
PAPIER = (245, 235, 210)
OMBRE = (180, 165, 140)
background = PAPIER

# BIOMES

DUNES = 0
CACTUS = 1
SABLE = 2
OASIS = 3
VILLAGE = 4
MINES = 5

noms_biomes = {
    DUNES: "Dunes",
    CACTUS: "Cactus",
    SABLE: "Sable",
    OASIS: "Oasis",
    VILLAGE: "Village",
    MINES: "Mines",
}


palette = {
    DUNES: (229, 140, 7),
    CACTUS: (18, 120, 40),
    SABLE: (250, 224, 75),
    OASIS: (62, 222, 219),
    VILLAGE: (92, 46, 16),
    MINES: (161, 161, 116),
}


# Polices et taille d'écriture
font = pygame.font.SysFont("Georgia", 15)
font_titre = pygame.font.SysFont("Georgia", 20)

# Emplacement du titre

Titre_x = 15
Titre_y = 15


# L'endroit ou on imprime la carte du monde
carte_sable = pygame.Surface(size)


# Variables de taille
rayon_max = 150
centre_x = largeur / 2
centre_y = hauteur / 2
taille_hex = 10
largeur_hex = math.sqrt(3) * taille_hex
hauteur_hex = 3 / 2 * taille_hex
marge = 5 * taille_hex

#


def draw_hexagon(surface, color, center, size, bord=0):
    points = []
    x0, y0 = center
    for i in range(6):
        angle = (
            math.pi / 3 * i + math.pi / 6
        )  # on enlève + math.pi / 6 si on veut un hexagone avec un plat en haut
        x = x0 + size * math.cos(angle)
        y = y0 + size * math.sin(angle)
        points.append((int(x), int(y)))  # valeurs entières pour moins de bugs visuels
    pygame.draw.polygon(
        surface, color, points, bord
    )  # le dernier paramètre est la largeur du trait, 0 remplit toute la figure
    # pygame.draw.polygon(surface, BLACK, points, 1)


def spirale(rayon):
    resultats = [(0, 0)]
    directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
    for i in range(1, rayon + 1):
        q = -i
        r = i

        for t in directions:
            drx, dry = t
            for a in range(i):
                resultats.append((q, r))
                q += drx
                r += dry

    return resultats


def choisir_biome(q, r, biomes):
    # distance_x = centre_x + largeur_hex * q + r / 2
    # distance_y = centre_y + largeur_hex * r
    voisins = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

    poids = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    # if distance_x > largeur - marge or distance_y > hauteur - marge:
    # return MER
    for dx, dy in voisins:
        voisin = (q + dx, r + dy)
        if voisin in biomes:
            biome_voisin = biomes[voisin]

            if biome_voisin == DUNES:
                poids[0] += 90
                poids[2] += 5
                poids[5] += 5

            elif biome_voisin == CACTUS:
                poids[1] += 15
                poids[2] += 80
                poids[4] += 5

            elif biome_voisin == SABLE:
                poids[2] += 90
                poids[0] += 5
                poids[1] += 5
                poids[4] += 5
            elif biome_voisin == OASIS:
                poids[3] += 80
                poids[4] += 3
                poids[1] += 17
            elif biome_voisin == VILLAGE:
                poids[4] += 92
                poids[3] += 2
                poids[2] += 3
                poids[5] += 3
            elif biome_voisin == MINES:
                poids[4] += 5
                poids[5] += 60
                poids[0] += 35

    total = sum(poids.values())
    tirage = random.uniform(0, total)

    cumul = 0
    for biome, p in poids.items():
        cumul += p
        if tirage <= cumul:
            return biome


"""
Exemple 0-----10-----13-----15
         Plaine  Forêt   Mer
Si tirage = 7 → plaine
Si tirage = 11 → forêt
Si tirage = 14 → Mer
"""


def spirale_dessin():
    return spirale(rayon_max)


matrice_sable = spirale_dessin()


def créa_spirale():
    # Choix des couleurs
    biomes = {}
    for q, r in matrice_sable:
        if (q, r) == (0, 0):
            biomes[(q, r)] = random.randint(0, 1)
        else:
            biomes[(q, r)] = choisir_biome(q, r, biomes)
    return biomes


biomes = créa_spirale()

carte_sable.fill(background)
for i in range(len(matrice_sable)):
    q, r = matrice_sable[i]
    x = largeur_hex * (q + r / 2)
    y = hauteur_hex * r
    couleur = palette[biomes[(q, r)]]
    draw_hexagon(carte_sable, couleur, (centre_x + x, centre_y + y), taille_hex)


def dessin_sable():
    screen.blit(carte_sable, (0, 0))  # on colle la carte précalculée sur l'écran

    # AFFICHER LE BIOME

    mx, my = pygame.mouse.get_pos()  # position de la souris
    couleur_pixel = carte_sable.get_at((mx, my))[:3]
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

    # AFFICHER LE TITRE

    Titre = font_titre.render("DÉSERT GÉNÉRÉ PAR INFLUENCE DES VOISINS", True, BLACK)
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

    caption = "MAPS 2D Monde"
    pygame.display.set_caption(caption)
