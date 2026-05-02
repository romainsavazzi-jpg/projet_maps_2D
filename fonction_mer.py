import pygame
import math
import random
from configuration import screen, size, largeur, hauteur

pygame.init()

BLACK = (0, 0, 0)
PAPIER = (245, 235, 210)
OMBRE = (180, 165, 140)
background = (20, 60, 140)

OCEAN = 0
ALGUES = 1
RECIF = 2
VILLAGE_SOUS_M = 3
POISSONS = 4
FOSSE = 5

noms_biomes = {
    OCEAN: "Océan",
    ALGUES: "Algues",
    RECIF: "Récif corallien",
    VILLAGE_SOUS_M: "Village sous-marin",
    POISSONS: "Banc de poissons",
    FOSSE: "Fosse abyssale",
}

palette = {
    OCEAN: (30, 90, 200),
    ALGUES: (20, 130, 60),
    RECIF: (230, 120, 50),
    VILLAGE_SOUS_M: (180, 160, 100),
    POISSONS: (80, 190, 210),
    FOSSE: (10, 20, 60),
}

font = pygame.font.SysFont("Georgia", 15)
font_titre = pygame.font.SysFont("Georgia", 20)

Titre_x = 15
Titre_y = 15

carte_mer = pygame.Surface(size)

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
    poids = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for dx, dy in voisins:
        voisin = (q + dx, r + dy)
        if voisin in biomes:
            biome_voisin = biomes[voisin]

            if biome_voisin == OCEAN:
                poids[0] += 200
                poids[1] += 1
                poids[2] += 1
                poids[3] += 5
                poids[4] += 1
                poids[5] += 1

            elif biome_voisin == ALGUES:
                poids[1] += 50
                poids[0] += 70
                poids[2] += 1
                poids[4] += 1
                poids[3] += 2

            elif biome_voisin == RECIF:
                poids[2] += 50
                poids[0] += 70
                poids[1] += 12

            elif biome_voisin == VILLAGE_SOUS_M:
                poids[3] += 70
                poids[0] += 50
                poids[1] += 10

            elif biome_voisin == POISSONS:
                poids[4] += 55
                poids[0] += 70
                poids[1] += 5

            elif biome_voisin == FOSSE:
                poids[5] += 90
                poids[0] += 5
                poids[4] += 5

    total = sum(poids.values())
    if total == 0:
        return OCEAN
    tirage = random.uniform(0, total)
    cumul = 0
    for biome, p in poids.items():
        cumul += p
        if tirage <= cumul:
            return biome


def spirale_dessin():
    return spirale(rayon_max)


matrice_mer = spirale_dessin()


def créa_spirale():
    biomes = {}
    for q, r in matrice_mer:
        if (q, r) == (0, 0):
            biomes[(q, r)] = OCEAN
        else:
            biomes[(q, r)] = choisir_biome(q, r, biomes)
    return biomes


biomes = créa_spirale()

carte_mer.fill(background)
for i in range(len(matrice_mer)):
    q, r = matrice_mer[i]
    x = largeur_hex * (q + r / 2)
    y = hauteur_hex * r
    couleur = palette[biomes[(q, r)]]
    draw_hexagon(carte_mer, couleur, (centre_x + x, centre_y + y), taille_hex)


def dessin_mer():
    screen.blit(carte_mer, (0, 0))

    mx, my = pygame.mouse.get_pos()
    couleur_pixel = carte_mer.get_at((mx, my))[:3]

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

    Titre = font_titre.render("MER GÉNÉRÉE PAR INFLUENCE DES VOISINS", True, BLACK)
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

    pygame.display.set_caption("MAPS 2D Mer")
