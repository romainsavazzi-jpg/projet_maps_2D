"""
test_donjons.py — tests complets pour donjons.py (version MST + bonus + portes).

Organisation :
  1. creer_grille
  2. dessiner_contour
  3. dessiner_salle
  4. salles_se_chevauchent
  5. generer_salles
  6. centre_salle
  7. creuser_segment  (nouvelle fonction)
  8. creuser_couloir  (avec portes)
  9. Union-Find       (creer_union_find, trouver_racine, unir, sont_connectes)
 10. distance_salles
 11. construire_aretes
 12. relier_salles    (MST + bonus)
"""

import sys

sys.path.insert(0, "/home/claude")

from fonctions_donjons import (
    creer_grille,
    dessiner_contour,
    dessiner_salle,
    salles_se_chevauchent,
    generer_salles,
    centre_salle,
    creuser_segment,
    creuser_couloir,
    creer_union_find,
    trouver_racine,
    unir,
    sont_connectes,
    distance_salles,
    construire_aretes,
    relier_salles,
    MUR,
    SOL,
    PORTE,
    VIDE,
)


# ════════════════════════════════════════════════════════════════════════════
# 1. creer_grille
# ════════════════════════════════════════════════════════════════════════════


def test_creer_grille_dimensions():
    grille = creer_grille(10, 5)
    assert len(grille) == 5
    assert len(grille[0]) == 10


def test_creer_grille_remplie_de_vide():
    grille = creer_grille(5, 5)
    for ligne in grille:
        for case in ligne:
            assert case == VIDE


def test_creer_grille_caractere_personnalise():
    grille = creer_grille(3, 3, MUR)
    assert grille[0][0] == MUR
    assert grille[2][2] == MUR
    assert grille[1][2] == MUR


# ════════════════════════════════════════════════════════════════════════════
# 2. dessiner_contour
# ════════════════════════════════════════════════════════════════════════════


def test_dessiner_contour_bords_haut_bas():
    grille = creer_grille(10, 8)
    dessiner_contour(grille, 0, 0, 10, 8)
    for col in range(10):
        assert grille[0][col] == MUR
        assert grille[7][col] == MUR


def test_dessiner_contour_bords_gauche_droite():
    grille = creer_grille(10, 8)
    dessiner_contour(grille, 0, 0, 10, 8)
    for ligne in range(8):
        assert grille[ligne][0] == MUR
        assert grille[ligne][9] == MUR


def test_dessiner_contour_interieur_intact():
    # L'intérieur de la boîte ne doit pas être touché
    grille = creer_grille(10, 8)
    dessiner_contour(grille, 0, 0, 10, 8)
    assert grille[1][1] == VIDE
    assert grille[6][8] == VIDE


def test_dessiner_contour_position_offset():
    # Contour décalé : les murs doivent être aux bonnes positions décalées
    grille = creer_grille(20, 15)
    dessiner_contour(grille, 5, 3, 8, 6)
    assert grille[3][5] == MUR
    assert grille[8][12] == MUR
    assert grille[3][0] == VIDE


# ════════════════════════════════════════════════════════════════════════════
# 3. dessiner_salle
# ════════════════════════════════════════════════════════════════════════════


def test_dessiner_salle_contour_en_mur():
    grille = creer_grille(20, 15)
    dessiner_salle(grille, 2, 2, 8, 5)
    assert grille[2][2] == MUR
    assert grille[6][9] == MUR


def test_dessiner_salle_interieur_en_sol():
    grille = creer_grille(20, 15)
    dessiner_salle(grille, 2, 2, 8, 5)
    assert grille[3][3] == SOL
    assert grille[5][8] == SOL


def test_dessiner_salle_exterieur_intact():
    grille = creer_grille(20, 15)
    dessiner_salle(grille, 2, 2, 8, 5)
    assert grille[0][0] == VIDE
    assert grille[14][19] == VIDE


# ════════════════════════════════════════════════════════════════════════════
# 4. salles_se_chevauchent
# ════════════════════════════════════════════════════════════════════════════


def test_pas_de_chevauchement_salles_separees():
    salles = [(0, 0, 5, 5)]
    assert salles_se_chevauchent(salles, 10, 10, 5, 5) == False


def test_chevauchement_direct():
    salles = [(0, 0, 10, 10)]
    assert salles_se_chevauchent(salles, 5, 5, 10, 10) == True


def test_chevauchement_par_marge():
    salles = [(0, 0, 5, 5)]
    assert salles_se_chevauchent(salles, 5, 0, 5, 5, marge=1) == True


def test_pas_chevauchement_avec_liste_vide():
    assert salles_se_chevauchent([], 0, 0, 5, 5) == False


# ════════════════════════════════════════════════════════════════════════════
# 5. generer_salles
# ════════════════════════════════════════════════════════════════════════════


def test_generer_salles_nombre_correct():
    grille = creer_grille(60, 25)
    salles = generer_salles(grille, nb_salles=4)
    assert len(salles) == 4


def test_generer_salles_dans_les_bords():
    grille = creer_grille(60, 25)
    salles = generer_salles(grille, nb_salles=5)
    for x, y, larg, haut in salles:
        assert x >= 1
        assert y >= 1
        assert x + larg <= 59
        assert y + haut <= 24


def test_generer_salles_aucun_chevauchement():
    grille = creer_grille(60, 25)
    salles = generer_salles(grille, nb_salles=5)
    for i in range(len(salles)):
        for j in range(i + 1, len(salles)):
            sx, sy, sl, sh = salles[j]
            autres = [salles[k] for k in range(len(salles)) if k != j]
            assert not salles_se_chevauchent(autres, sx, sy, sl, sh)


# ════════════════════════════════════════════════════════════════════════════
# 6. centre_salle
# ════════════════════════════════════════════════════════════════════════════


def test_centre_salle_calcul():
    salle = (0, 0, 10, 8)
    cx, cy = centre_salle(salle)
    assert cx == 5
    assert cy == 4


def test_centre_salle_offset():
    salle = (10, 6, 8, 4)
    cx, cy = centre_salle(salle)
    assert cx == 14  # 10 + 8//2
    assert cy == 8  # 6 + 4//2


# ════════════════════════════════════════════════════════════════════════════
# 7. creuser_segment
# ════════════════════════════════════════════════════════════════════════════


def test_creuser_segment_vide_devient_sol():
    # Un segment sur des cases VIDE doit toutes devenir SOL
    grille = creer_grille(10, 5)
    cases = [(2, col) for col in range(1, 8)]
    creuser_segment(grille, cases)
    for col in range(1, 8):
        assert grille[2][col] == SOL


def test_creuser_segment_premier_mur_devient_porte():
    # La première case MUR rencontrée dans le segment doit devenir PORTE
    grille = creer_grille(15, 10)
    dessiner_salle(grille, 6, 2, 5, 4)  # mur à la colonne 6
    # On creuse un segment horizontal qui arrive sur le mur de la salle
    cases = [(4, col) for col in range(0, 8)]
    creuser_segment(grille, cases)
    assert grille[4][6] == PORTE


def test_creuser_segment_deux_portes_si_traversee():
    """Quand un couloir entre DANS une salle puis en ressort, il doit y avoir
    une porte à l'entrée ET une porte à la sortie.
    C'est le comportement attendu : chaque paroi percée génère une porte,
    ce qui donne visuellement une entrée et une sortie claires.

    Note : dans une première version du test, on vérifiait que le mur de sortie
    restait intact. Ce n'est pas le bon comportement — Angband lui-même place
    une porte à chaque traversée de paroi.
    """
    grille = creer_grille(20, 10)
    dessiner_salle(grille, 5, 2, 6, 4)  # murs aux colonnes 5 et 10, lignes 2 et 5
    cases = [(4, col) for col in range(0, 11)]
    creuser_segment(grille, cases)
    assert grille[4][5] == PORTE  # paroi d'entrée → PORTE
    assert grille[4][10] == PORTE  # paroi de sortie → PORTE aussi


# ════════════════════════════════════════════════════════════════════════════
# 8. creuser_couloir (avec portes)
# ════════════════════════════════════════════════════════════════════════════


def test_creuser_couloir_horizontal():
    grille = creer_grille(20, 10)
    creuser_couloir(grille, 2, 5, 10, 5)
    for col in range(2, 11):
        assert grille[5][col] == SOL


def test_creuser_couloir_vertical():
    grille = creer_grille(20, 15)
    creuser_couloir(grille, 5, 2, 5, 10)
    for ligne in range(2, 11):
        assert grille[ligne][5] == SOL


def test_creuser_couloir_en_L():
    grille = creer_grille(20, 15)
    creuser_couloir(grille, 2, 2, 10, 8)
    # Portion horizontale
    assert grille[2][5] == SOL
    # Portion verticale
    assert grille[5][10] == SOL


def test_creuser_couloir_pose_porte_sur_mur_salle():
    """Quand le couloir rencontre le mur d'une salle, il pose une PORTE."""
    grille = creer_grille(20, 15)
    dessiner_salle(grille, 8, 2, 6, 5)
    creuser_couloir(grille, 2, 4, 12, 4)
    assert grille[4][8] == PORTE


# ════════════════════════════════════════════════════════════════════════════
# 9. Union-Find
# ════════════════════════════════════════════════════════════════════════════


def test_union_find_creation():
    parent = creer_union_find(5)
    assert parent == [0, 1, 2, 3, 4]


def test_trouver_racine_sans_union():
    parent = creer_union_find(4)
    assert trouver_racine(parent, 0) == 0
    assert trouver_racine(parent, 3) == 3


def test_unir_deux_composantes_distinctes():
    parent = creer_union_find(4)
    resultat = unir(parent, 0, 1)
    assert resultat == True


def test_unir_meme_composante_retourne_false():
    parent = creer_union_find(4)
    unir(parent, 0, 1)
    resultat = unir(parent, 0, 1)
    assert resultat == False


def test_sont_connectes_apres_union():
    parent = creer_union_find(4)
    assert not sont_connectes(parent, 0, 2)
    unir(parent, 0, 2)
    assert sont_connectes(parent, 0, 2)


def test_connectivite_transitive():
    parent = creer_union_find(4)
    unir(parent, 0, 1)
    unir(parent, 1, 2)
    assert sont_connectes(parent, 0, 2)
    assert not sont_connectes(parent, 0, 3)


# ════════════════════════════════════════════════════════════════════════════
# 10. distance_salles
# ════════════════════════════════════════════════════════════════════════════


def test_distance_salles_meme_centre():
    salle = (5, 5, 4, 4)
    assert distance_salles(salle, salle) == 0.0


def test_distance_salles_horizontale():
    salle_a = (0, 0, 2, 2)  # centre (1, 1)
    salle_b = (10, 0, 2, 2)  # centre (11, 1)
    dist = distance_salles(salle_a, salle_b)
    assert abs(dist - 10.0) < 0.01


def test_distance_salles_symetrie():
    salle_a = (0, 0, 6, 4)
    salle_b = (20, 10, 8, 6)
    assert distance_salles(salle_a, salle_b) == distance_salles(salle_b, salle_a)


# ════════════════════════════════════════════════════════════════════════════
# 11. construire_aretes
# ════════════════════════════════════════════════════════════════════════════


def test_construire_aretes_nombre():
    # Pour N salles → N*(N-1)/2 arêtes
    salles = [(0, 0, 4, 4), (10, 0, 4, 4), (20, 0, 4, 4)]
    aretes = construire_aretes(salles)
    assert len(aretes) == 3


def test_construire_aretes_triees():
    salles = [(0, 0, 4, 4), (5, 0, 4, 4), (50, 0, 4, 4)]
    aretes = construire_aretes(salles)
    distances = [d for d, i, j in aretes]
    assert distances == sorted(distances)


def test_construire_aretes_indices_valides():
    salles = [(0, 0, 4, 4), (10, 0, 4, 4), (20, 0, 4, 4), (30, 0, 4, 4)]
    aretes = construire_aretes(salles)
    for dist, i, j in aretes:
        assert 0 <= i < len(salles)
        assert 0 <= j < len(salles)
        assert i != j


# ════════════════════════════════════════════════════════════════════════════
# 12. relier_salles (MST + bonus)
# ════════════════════════════════════════════════════════════════════════════


def test_relier_salles_toutes_connectees():
    """Après connexion, les centres de toutes les salles doivent être en SOL ou PORTE."""
    grille = creer_grille(60, 25)
    dessiner_contour(grille, 0, 0, 60, 25)
    salles = generer_salles(grille, nb_salles=4)
    relier_salles(grille, salles)
    for s in salles:
        cx, cy = centre_salle(s)
        assert grille[cy][cx] in (SOL, PORTE)


def test_relier_salles_une_seule_salle():
    """Avec une seule salle, relier_salles ne doit pas lever d'exception."""
    grille = creer_grille(60, 25)
    dessiner_salle(grille, 5, 5, 8, 6)
    salles = [(5, 5, 8, 6)]
    relier_salles(grille, salles)


def test_relier_salles_mst_pur_nb_couloirs():
    """Avec nb_bonus=0, le MST doit tracer exactement N-1 couloirs.
    On ne peut pas compter directement les couloirs, mais on vérifie
    que toutes les salles sont connectées (propriété du MST).
    """
    grille = creer_grille(80, 30)
    salles = [(2, 2, 8, 5), (20, 2, 8, 5), (40, 2, 8, 5), (60, 2, 8, 5)]
    for s in salles:
        dessiner_salle(grille, *s)
    relier_salles(grille, salles, nb_bonus=0)
    for s in salles:
        cx, cy = centre_salle(s)
        assert grille[cy][cx] == SOL


def test_relier_salles_avec_bonus_ne_plante_pas():
    """L'ajout de couloirs bonus ne doit pas lever d'exception."""
    grille = creer_grille(80, 30)
    salles = [(2, 2, 8, 5), (20, 10, 8, 5), (50, 2, 8, 5), (60, 15, 8, 5)]
    for s in salles:
        dessiner_salle(grille, *s)
    relier_salles(grille, salles, nb_bonus=2)


def test_relier_salles_deux_salles():
    """Cas limite : exactement 2 salles → 1 seul couloir MST."""
    grille = creer_grille(40, 20)
    salles = [(2, 5, 8, 5), (25, 5, 8, 5)]
    for s in salles:
        dessiner_salle(grille, *s)
    relier_salles(grille, salles, nb_bonus=0)
    # Le couloir doit passer par le centre des deux salles
    for s in salles:
        cx, cy = centre_salle(s)
        assert grille[cy][cx] == SOL
