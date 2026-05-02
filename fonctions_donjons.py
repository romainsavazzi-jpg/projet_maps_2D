import pygame
import random
import math
from configuration import screen, largeur, hauteur


BLACK = (0, 0, 0)
PAPIER = (245, 235, 210)
OMBRE = (180, 165, 140)

# Polices et taille d'écriture
font = pygame.font.SysFont("Georgia", 15)
font_titre = pygame.font.SysFont("Georgia", 20)

Titre_x = 15
Titre_y = 15


MAP_LARG = 60
MAP_HAUT = 25
TAILLE_CASE = 24

FENETRE_LARG = MAP_LARG * TAILLE_CASE
FENETRE_HAUT = MAP_HAUT * TAILLE_CASE

carte_donjon = pygame.Surface((FENETRE_LARG, FENETRE_HAUT))


NOIR = (0, 0, 0)
MUR_COULEUR = (80, 80, 100)  # gris
SOL_COULEUR = (40, 30, 20)  # brun très sombre
PORTE_COULEUR = (180, 130, 50)  # doré
VIDE_COULEUR = (0, 0, 0)  # noir


MUR = "#"
SOL = "."
PORTE = "+"
VIDE = " "


# ── Grille ────────────────────────────────────────────────────────────────────


def creer_grille(largeur, hauteur, caractere=VIDE):
    return [[caractere for _ in range(largeur)] for _ in range(hauteur)]


def dessiner_contour(grille, x, y, largeur, hauteur):
    for col in range(x, x + largeur):
        grille[y][col] = MUR
        grille[y + hauteur - 1][col] = MUR
    for ligne in range(y, y + hauteur):
        grille[ligne][x] = MUR
        grille[ligne][x + largeur - 1] = MUR


def dessiner_salle(grille, x, y, largeur, hauteur):
    dessiner_contour(grille, x, y, largeur, hauteur)
    for ligne in range(y + 1, y + hauteur - 1):
        for col in range(x + 1, x + largeur - 1):
            grille[ligne][col] = SOL


def salles_se_chevauchent(salles, x, y, largeur, hauteur, marge=1):
    for sx, sy, sl, sh in salles:
        if not (
            (x + largeur + marge <= sx or sx + sl + marge <= x)
            or (y + hauteur + marge <= sy or sy + sh + marge <= y)
        ):
            return True
    return False


def generer_salles(grille, nb_salles=6, max_tentatives=100):
    G_HAUTEUR = len(grille)
    G_LARGEUR = len(grille[0])
    salles_placees = []
    for _ in range(nb_salles):
        for _ in range(max_tentatives):
            s_larg = random.randint(6, 12)
            s_haut = random.randint(4, 7)
            x = random.randint(1, G_LARGEUR - s_larg - 1)
            y = random.randint(1, G_HAUTEUR - s_haut - 1)
            if not salles_se_chevauchent(salles_placees, x, y, s_larg, s_haut):
                dessiner_salle(grille, x, y, s_larg, s_haut)
                salles_placees.append((x, y, s_larg, s_haut))
                break
    return salles_placees


def centre_salle(salle):
    x, y, larg, haut = salle
    return (x + larg // 2, y + haut // 2)


# ── Couloir avec portes ───────────────────────────────────────────────────────


def creuser_segment(grille, cases):
    """Parcourt une liste de (ligne, col) et creuse le couloir.

    Règle pour les portes :
    - Si la case est VIDE → on pose du SOL (couloir).
    - Si la case est MUR  → on pose une PORTE (entrée/sortie de salle),
      MAIS seulement la première fois qu'on rencontre un mur consécutif.
      Le deuxième mur consécutif n'est PAS modifié (on ne perce pas
      l'autre côté du couloir de salle).

    Difficulté rencontrée : avec l'ancienne logique, TOUS les murs
    rencontrés étaient transformés, ce qui perçait plusieurs fois
    les parois et donnait des ouvertures multiples. La solution est
    de détecter la transition VIDE→MUR pour placer exactement une porte.
    """
    dans_mur = False
    for ligne, col in cases:
        case = grille[ligne][col]
        if case == VIDE:
            grille[ligne][col] = SOL
            dans_mur = False
        elif case == MUR:
            if not dans_mur:
                # Première case MUR rencontrée : c'est la paroi → PORTE
                grille[ligne][col] = PORTE
                dans_mur = True
            # Si on était déjà dans un mur (mur épais), on ne touche pas
        elif case in (SOL, PORTE):
            # On entre dans une salle ou un couloir existant : on s'arrête
            dans_mur = False


def creuser_couloir(grille, x1, y1, x2, y2):
    """Creuse un couloir en L de (x1,y1) à (x2,y2).
    D'abord horizontalement jusqu'à (x2, y1), puis verticalement jusqu'à (x2, y2).
    Gère les portes via creuser_segment.
    """
    # Segment horizontal
    pas_x = 1 if x2 >= x1 else -1
    segment_h = [(y1, col) for col in range(x1, x2 + pas_x, pas_x)]

    # Segment vertical (on évite de dupliquer le coude)
    pas_y = 1 if y2 >= y1 else -1
    segment_v = [(ligne, x2) for ligne in range(y1, y2 + pas_y, pas_y)]

    creuser_segment(grille, segment_h)
    creuser_segment(grille, segment_v)


# ── Union-Find ────────────────────────────────────────────────────────────────


def creer_union_find(n):
    """Crée une structure Union-Find pour n éléments (chacun est sa propre racine)."""
    return list(range(n))


def trouver_racine(parent, i):
    """Remonte jusqu'à la racine avec compression de chemin."""
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def unir(parent, i, j):
    """Fusionne les ensembles de i et j. Retourne False s'ils étaient déjà unis."""
    ri, rj = trouver_racine(parent, i), trouver_racine(parent, j)
    if ri == rj:
        return False
    parent[ri] = rj
    return True


def sont_connectes(parent, i, j):
    return trouver_racine(parent, i) == trouver_racine(parent, j)


# ── MST + couloirs bonus ──────────────────────────────────────────────────────


def distance_salles(salle_a, salle_b):
    cx1, cy1 = centre_salle(salle_a)
    cx2, cy2 = centre_salle(salle_b)
    return math.sqrt((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2)


def construire_aretes(salles):
    """Toutes les arêtes possibles entre salles, triées par distance croissante."""
    aretes = []
    for i in range(len(salles)):
        for j in range(i + 1, len(salles)):
            dist = distance_salles(salles[i], salles[j])
            aretes.append((dist, i, j))
    aretes.sort()
    return aretes


def relier_salles(grille, salles, nb_bonus=2):
    """Relie les salles : MST (arbre couvrant minimal) + quelques couloirs bonus.

    Étape 1 — MST avec Kruskal :
        On parcourt les arêtes triées par distance et on ajoute une arête
        seulement si elle relie deux composantes distinctes (Union-Find).
        Résultat : N-1 couloirs, réseau connexe minimal.

    Étape 2 — Couloirs bonus (inspiré d'Angband) :
        Après le MST, on ajoute nb_bonus arêtes supplémentaires choisies
        aléatoirement parmi les arêtes restantes (non utilisées dans le MST),
        en favorisant les plus courtes. Cela crée des boucles dans la carte
        et évite la linéarité d'un arbre pur.

    Paramètre nb_bonus : nombre de couloirs bonus à ajouter (défaut 2).
    Mettre 0 pour un MST pur.
    """
    if len(salles) < 2:
        return

    aretes = construire_aretes(salles)
    parent = creer_union_find(len(salles))

    aretes_mst = []
    aretes_restantes = []

    for dist, i, j in aretes:
        if unir(parent, i, j):
            aretes_mst.append((dist, i, j))
            cx1, cy1 = centre_salle(salles[i])
            cx2, cy2 = centre_salle(salles[j])
            creuser_couloir(grille, cx1, cy1, cx2, cy2)
        else:
            aretes_restantes.append((dist, i, j))

    # Couloirs bonus : on prend parmi les arêtes restantes les plus courtes
    # (les salles les plus proches non encore reliées directement).
    # On en choisit au maximum nb_bonus, ou toutes s'il en reste moins.
    candidats = aretes_restantes[: max(nb_bonus * 3, len(aretes_restantes))]
    bonus_choisis = random.sample(candidats, min(nb_bonus, len(candidats)))

    for dist, i, j in bonus_choisis:
        cx1, cy1 = centre_salle(salles[i])
        cx2, cy2 = centre_salle(salles[j])
        creuser_couloir(grille, cx1, cy1, cx2, cy2)


# ── Rendu ─────────────────────────────────────────────────────────────────────


def couleur_case(caractere):
    if caractere == MUR:
        return MUR_COULEUR
    if caractere == SOL:
        return SOL_COULEUR
    if caractere == PORTE:
        return PORTE_COULEUR
    return VIDE_COULEUR


def nouvelle_map():
    g = creer_grille(MAP_LARG, MAP_HAUT)
    dessiner_contour(g, 0, 0, MAP_LARG, MAP_HAUT)
    salles = generer_salles(g, nb_salles=6)
    relier_salles(g, salles)
    return g


grille = nouvelle_map()


def dessiner_donjon():
    carte_donjon.fill(NOIR)
    for y, ligne in enumerate(grille):
        for x, case in enumerate(ligne):
            couleur = couleur_case(case)
            rect = pygame.Rect(
                x * TAILLE_CASE,
                y * TAILLE_CASE,
                TAILLE_CASE,
                TAILLE_CASE,
            )
            pygame.draw.rect(carte_donjon, couleur, rect)
    cx = (largeur - FENETRE_LARG) // 2
    cy = (hauteur - FENETRE_HAUT) // 2

    Titre = font_titre.render("Un super donjon", True, BLACK)
    largeur_titre, hauteur_titre = Titre.get_size()
    pygame.draw.rect(
        carte_donjon,
        BLACK,
        (Titre_x - 7, Titre_y - 7, largeur_titre + 16, hauteur_titre + 16),
    )
    pygame.draw.rect(
        carte_donjon,
        OMBRE,
        (Titre_x - 6, Titre_y - 6, largeur_titre + 14, hauteur_titre + 14),
    )
    pygame.draw.rect(
        carte_donjon,
        PAPIER,
        (Titre_x - 4, Titre_y - 4, largeur_titre + 10, hauteur_titre + 10),
    )
    carte_donjon.blit(Titre, (Titre_x, Titre_y))
    screen.fill(NOIR)
    screen.blit(carte_donjon, (cx, cy))


def regenerer_donjon():
    global grille
    grille = nouvelle_map()
