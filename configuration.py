import pygame

pygame.init()

# Paramètres de l'écran
info = pygame.display.Info()
largeur = info.current_w
hauteur = info.current_h
size = largeur, hauteur
screen = pygame.display.set_mode(size)
