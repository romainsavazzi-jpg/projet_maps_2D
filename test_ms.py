import pygame
import numpy as np
from fonctions_MS_CM import Marching_squares, Catmull_Rom

# Ceci est un fichier de test si vous voulez vous amuser avec ou essayer de détecter encore plus de bugs

Map = [[0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 1, 1, 1, 0, 4, 4, 4, 0],
       [0, 1, 1, 1, 1, 1, 0, 0, 4, 0],
       [0, 5, 1, 1, 1, 1, 1, 0, 4, 0],
       [0, 5, 5, 0, 1, 0, 0, 0, 0, 0],
       [0, 5, 5, 5, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
       [0, 3, 3, 3, 0, 2, 2, 0, 0, 0],
       [0, 3, 3, 0, 0, 2, 2, 0, 0, 0],
       [0, 3, 3, 0, 0, 0, 0, 0, 0, 0]]
# Map = [[0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
#        [0, 0, 1, 1, 1, 0, 0, 0, 4, 0],
#        [0, 1, 1, 1, 1, 1, 0, 0, 4, 0],
#        [0, 5, 1, 1, 1, 1, 1, 0, 4, 0],
#        [0, 5, 5, 0, 1, 0, 0, 0, 0, 0],
#        [0, 5, 5, 5, 0, 0, 0, 0, 0, 0],
#        [0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
#        [0, 0, 3, 3, 0, 2, 2, 0, 0, 0],
#        [0, 0, 3, 0, 0, 2, 2, 0, 0, 0],
#        [0, 0, 3, 0, 0, 0, 0, 0, 0, 0]]

# Map0 = [[0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
#        [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
#        [0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
#        [0, 5, 1, 1, 1, 1, 1, 0, 0, 0],
#        [0, 5, 5, 0, 1, 0, 0, 0, 0, 0],
#        [0, 5, 5, 5, 0, 0, 0, 0, 0, 0],
#        [0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
#        [0, 0, 3, 3, 0, 2, 2, 0, 0, 0],
#        [0, 0, 3, 0, 0, 2, 2, 0, 0, 0],
#        [0, 0, 3, 0, 0, 0, 0, 0, 0, 0]]


ALL_MS = {n: Marching_squares(Map, n) for n in range(1, 6)}
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True
screen.fill((30, 30, 30))
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for n in range(1, 6):
        MS = ALL_MS[n]

        for c in MS:
            if len(c) < 3:
                continue

            points = [(x * 50 + 50, y * 50 + 50) for (x, y) in c]

            if abs(points[0][0] - points[-1][0]) > 1e-3 or abs(points[0][1] - points[-1][1]) > 1e-3:
                points.append(points[0])

            # pygame.draw.lines(screen, "white", True, points, 2)

            if len(points) < 4:
                continue

            points_ext = [points[-2]] + points + [points[1]]

            curve = []
            for i in range(len(points_ext) - 3):
                for t in np.linspace(0, 1, 50):
                    curve.append(Catmull_Rom(
                        points_ext[i],
                        points_ext[i + 1],
                        points_ext[i + 2],
                        points_ext[i + 3],
                        t))

            if len(curve) > 1:
                pygame.draw.lines(screen, "red", False, curve, 3)

    pygame.display.flip()
