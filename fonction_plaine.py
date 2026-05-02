import pygame
import math
import random
from configuration import screen, size, largeur, hauteur

pygame.init()

BLACK = (0, 0, 0)
PAPIER = (245, 235, 210)
OMBRE = (180, 165, 140)
background = (160, 210, 130)

HERBE = 0
FORET = 1
RIVIERE = 2
VILLAGE = 3
COLLINES = 4

noms_biomes = {
    HERBE: "Herbe",
    FORET: "Forêt",
    RIVIERE: "Rivière",
    VILLAGE: "Village",
    COLLINES: "Collines",
}

palette = {
    HERBE: (140, 210, 100),
    FORET: (30, 110, 30),
    RIVIERE: (50, 130, 210),
    VILLAGE: (92, 46, 16),
    COLLINES: (180, 160, 90),
}

font = pygame.font.SysFont("Georgia", 15)
font_titre = pygame.font.SysFont("Georgia", 20)

Titre_x = 15
Titre_y = 15

carte_plaine = pygame.Surface(size)

rayon_max = 150
centre_x = largeur / 2
centre_y = hauteur / 2
taille_hex = 10
largeur_hex = math.sqrt(3) * taille_hex
hauteur_hex = 3 / 2 * taille_hex


def draw_hexagon(surface, color, center, size, bord=0):
    points = []
    x0, y0 = center
    for i in range(6):
        angle = math.pi / 3 * i + math.pi / 6
        x = x0 + size * math.cos(angle)
        y = y0 + size * math.sin(angle)
        points.append((int(x), int(y)))
    pygame.draw.polygon(surface, color, points, bord)


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
    voisins = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
    poids = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

    for dx, dy in voisins:
        voisin = (q + dx, r + dy)
        if voisin in biomes:
            biome_voisin = biomes[voisin]

            if biome_voisin == HERBE:
                poids[0] += 75
                poids[1] += 10
                poids[2] += 5
                poids[3] += 5
                poids[4] += 5

            elif biome_voisin == FORET:
                poids[1] += 70
                poids[0] += 20
                poids[4] += 8
                poids[2] += 2

            elif biome_voisin == RIVIERE:
                poids[2] += 70
                poids[0] += 20
                poids[1] += 8
                poids[3] += 2

            elif biome_voisin == VILLAGE:
                poids[3] += 55
                poids[0] += 30
                poids[2] += 10
                poids[1] += 5

            elif biome_voisin == COLLINES:
                poids[4] += 65
                poids[0] += 20
                poids[1] += 15

    total = sum(poids.values())
    if total == 0:
        return HERBE
    tirage = random.uniform(0, total)
    cumul = 0
    for biome, p in poids.items():
        cumul += p
        if tirage <= cumul:
            return biome


def spirale_dessin():
    return spirale(rayon_max)


matrice_plaine = spirale_dessin()


def créa_spirale():
    biomes = {}
    for q, r in matrice_plaine:
        if (q, r) == (0, 0):
            biomes[(q, r)] = HERBE
        else:
            biomes[(q, r)] = choisir_biome(q, r, biomes)
    return biomes


biomes = créa_spirale()

carte_plaine.fill(background)
for i in range(len(matrice_plaine)):
    q, r = matrice_plaine[i]
    x = largeur_hex * (q + r / 2)
    y = hauteur_hex * r
    couleur = palette[biomes[(q, r)]]
    draw_hexagon(carte_plaine, couleur, (centre_x + x, centre_y + y), taille_hex)


def dessin_plaine():
    screen.blit(carte_plaine, (0, 0))

    mx, my = pygame.mouse.get_pos()
    couleur_pixel = carte_plaine.get_at((mx, my))[:3]

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

    Titre = font_titre.render("PLAINE GÉNÉRÉE PAR INFLUENCE DES VOISINS", True, BLACK)
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

    pygame.display.set_caption("MAPS 2D Plaine")
