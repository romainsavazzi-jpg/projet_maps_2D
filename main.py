import pygame
from fonctions_monde import dessin_monde
from fonction_lancer import lancer, bouton_1, bouton_2
from fonction_sable import dessin_sable
from fonction_foret import dessin_foret
from fonction_plaine import dessin_plaine
from fonction_neige import dessin_neige
from fonction_mer import dessin_mer
from fonction_montagne import dessin_montagne
from fonctions_village import (
    dessin_village,
    regenerer_village,
    generate_village,
    BROWN,
)
from fonctions_maison import dessin_maison, set_events
from configuration import screen
from fonctions_donjons import dessiner_donjon, regenerer_donjon
from fonctions_paquets_d_onde import dessin_onde


pygame.init()
running = True

SABLE = (248, 222, 126)
FORET = (20, 120, 20)
PLAINE = (120, 200, 120)
NEIGE = (254, 254, 226)
MER = (40, 80, 200)
MONTAGNE = (200, 210, 210)
CAVE = (155, 148, 138)
VILLAGE = (92, 46, 16)
VILLAGE_M = (180, 160, 100)


lancement = True
monde = False
sable = False
foret = False
plaine = False
village = False
vide = False
maison = False
donjon = False
onde = False
neige = False
montagne = False
mer = False


while running:
    events = pygame.event.get()
    set_events(
        events
    )  # On récupère les évènement qu'une fois car on avait besoin de les récupérer aussi dans la génération de maison sauf que si on fait get.event deux fois dans la même frame la deuxième fois q'uon l'appelle on récu^père une liste vde car get vide la liste d'event.

    if lancement:
        lancer()
    elif monde:
        dessin_monde()
    elif sable:
        dessin_sable()
    elif foret:
        dessin_foret()
    elif plaine:
        dessin_plaine()
    elif neige:
        dessin_neige()
    elif montagne:
        dessin_montagne()
    elif mer:
        dessin_mer()
    elif village:
        dessin_village()
    elif maison:
        dessin_maison()
    elif donjon:
        dessiner_donjon()
    elif onde:
        dessin_onde()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if sable:
                if event.key == pygame.K_v:
                    sable = False
                    village = True
                    generate_village()
            if village:
                if event.key == pygame.K_r:  # régénérer village
                    regenerer_village()
                    generate_village()
            if donjon:
                if event.key == pygame.K_r:  # touche R → régénère une nouvelle map
                    regenerer_donjon()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if bouton_1.collidepoint(event.pos) and lancement:
                lancement = False
                monde = True
            elif bouton_2.collidepoint(event.pos) and lancement:
                lancement = False
                onde = True
            elif (
                monde or onde
            ):  # On vérifie le clic sur la map seulement si on est dans un des deux mondes
                couleur_clic = screen.get_at(event.pos)[:3]
                if couleur_clic == SABLE:
                    monde = False
                    onde = False
                    sable = True
                if couleur_clic == FORET:
                    onde = False
                    monde = False
                    foret = True
                if couleur_clic == PLAINE:
                    onde = False
                    monde = False
                    plaine = True
                if couleur_clic == NEIGE:
                    onde = False
                    monde = False
                    neige = True
                if couleur_clic == MER:
                    onde = False
                    monde = False
                    mer = True
                if couleur_clic == MONTAGNE:
                    onde = False
                    monde = False
                    montagne = True
            elif sable or foret or plaine or neige or mer or montagne:
                couleur_clic = screen.get_at(event.pos)[:3]
                if couleur_clic == VILLAGE or VILLAGE_M:
                    sable = False
                    foret = False
                    plaine = False
                    neige = False
                    mer = False
                    montagne = False
                    village = True
                    generate_village()

            elif village:
                couleur_clic = screen.get_at(event.pos)[:3]
                if couleur_clic == BROWN:
                    maison = True
                    village = False
            elif maison:
                couleur_clic = screen.get_at(event.pos)[:3]
                if couleur_clic == CAVE:
                    maison = False
                    donjon = True
    pygame.display.flip()
pygame.quit()
