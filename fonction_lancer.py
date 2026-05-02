import pygame
from configuration import screen, largeur, hauteur

# COULEURS
pygame.init()

BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (200, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PIF = (255, 100, 15)
PAPIER = (245, 235, 210)
OMBRE = (180, 165, 140)
PAPIER = (245, 235, 210)
MARRON = (59, 46, 30)
MARRON_CLAIR = (107, 79, 53)

font_titre = pygame.font.SysFont("Georgia", 52)
font_sous = pygame.font.SysFont("Georgia", 20)
font_bouton = pygame.font.SysFont("Georgia", 14)
bouton_1 = pygame.Rect(largeur // 2 - 210, hauteur // 2 - 25, 200, 50)
bouton_2 = pygame.Rect(largeur // 2 + 10, hauteur // 2 - 25, 200, 50)
lance = False


def lancer():
    screen.fill(PAPIER)

    # Titre
    titre = font_titre.render("PROJET GÉNÉRATION DE MAPS 2D", True, MARRON)
    screen.blit(titre, (largeur // 2 - titre.get_width() // 2, hauteur // 4))

    # Sous-titre
    sous = font_sous.render(
        "PARRA Timothée , AGUADO Antonin , BARZIC Isis , PICON Luca , EYMERIC Maxime , SAVAZZI Romain",
        True,
        MARRON_CLAIR,
    )
    screen.blit(sous, (largeur // 2 - sous.get_width() // 2, hauteur // 3))

    souris = pygame.mouse.get_pos()

    # Bouton qui change de couleur au survol

    survol1 = bouton_1.collidepoint(souris)  # si la souris touche le bouton
    pygame.draw.rect(screen, MARRON_CLAIR if survol1 else MARRON, bouton_1)
    texte_bouton1 = font_bouton.render("Génération par poids", True, PAPIER)
    screen.blit(
        texte_bouton1,
        (
            bouton_1.centerx - texte_bouton1.get_width() // 2,
            bouton_1.centery - texte_bouton1.get_height() // 2,
        ),
    )

    survol2 = bouton_2.collidepoint(souris)
    pygame.draw.rect(screen, MARRON_CLAIR if survol2 else MARRON, bouton_2)
    texte_bouton2 = font_bouton.render("Génération par paquet d'onde", True, PAPIER)
    screen.blit(
        texte_bouton2,
        (
            bouton_2.centerx - texte_bouton2.get_width() // 2,
            bouton_2.centery - texte_bouton2.get_height() // 2,
        ),
    )
