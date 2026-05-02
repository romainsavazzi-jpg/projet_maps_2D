from fonctions_village import (
    place_well,
    generate_roads,
    can_place_house,
    place_house,
    generate_houses,
    generate_trees,
    generate_village,
    draw,
    regenerer_village,
    decaler_gauche,
)
from fonctions_village import GRID_SIZE, HOUSE, EMPTY, TREE
from fonctions_village import limite_bordure


def test_place_well_limits():
    assert limite_bordure <= place_well()[0] <= GRID_SIZE - limite_bordure
    assert limite_bordure <= place_well()[1] <= GRID_SIZE - limite_bordure


def test_maisons_se_touchent_pas():
    grid = generate_village()
    compt_house_x = 0
    compt_house_y = 0
    a_la_suite_x = False
    a_la_suite_y = False
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] == HOUSE:
                compt_house_x += 1
                a_la_suite_x = True
            if not (a_la_suite_x):
                compt_house_x = 0
            a_la_suite_x = False
            if grid[x][y] == HOUSE:
                compt_house_y += 1
                a_la_suite_y = True
            if not (a_la_suite_y):
                compt_house_y = 0
            a_la_suite_y = False
            if compt_house_x >= 3 or compt_house_y >= 3:
                assert False
    assert True


def test_decaler_gauche_vide():
    grid = generate_village()
    grid, division_map = decaler_gauche()
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE // division_map):
            if grid[y][x] != EMPTY:
                assert False
    assert True


def test_proportion_generate_trees():
    grid = generate_village()
    compt_tree = 0
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] == TREE:
                compt_tree += 1
    if compt_tree < (1 / 2) * (GRID_SIZE**2):
        assert True
    else:
        assert False


def test_regenerer_village():
    grid = generate_village()
    grid = regenerer_village()
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] != EMPTY:
                assert False
    assert True
