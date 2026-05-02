from fonctions_monde import spirale, choisir_biome


def test_hexagone():
    assert True


def test_spirale():
    assert spirale(0) == [(0, 0)]
    assert spirale(1) == [(0, 0), (-1, 1), (0, 1), (1, 0), (1, -1), (0, -1), (-1, 0)]


def test_biome():
    assert (
        choisir_biome(0, 1, {(0, 0): 2})
    ) == 2  # si il y'a que de la mer en voisin on a de la mer
    assert (
        choisir_biome(0, 1, {(0, 0): 0})
    ) != 2  # il n'y a pas de mer à coté de la plaine
    assert (choisir_biome(0, 1, {(0, 0): 5})) == 4 or 5
