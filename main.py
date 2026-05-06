import pygame
from configuration import screen, largeur, hauteur

from fonctions_monde import dessin_monde, genere_et_dessine_carte_monde
from fonction_lancer import lancer, bouton_1, bouton_2
from fonction_sable import dessin_sable, genere_et_dessine_carte_sable
from fonction_foret import dessin_foret, genere_et_dessine_carte_foret
from fonction_plaine import dessin_plaine, genere_et_dessine_carte_plaine
from fonction_neige import dessin_neige, genere_et_dessine_carte_neige
from fonction_mer import dessin_mer, genere_et_dessine_carte_mer
from fonction_montagne import dessin_montagne, genere_et_dessine_carte_montagne
from fonctions_village import (
    dessin_village,
    regenerer_village,
    generate_village,
    dessine_carte_village,
    BROWN,
)
from fonctions_maison import dessin_maison, set_events
from fonctions_donjons import dessiner_donjon, regenerer_donjon
from fonctions_paquets_d_onde import dessin_onde, _nouvelle_grille, genere_et_dessine_carte_onde

pygame.init()

font = pygame.font.SysFont("Georgia", 20)
screen.fill((20, 20, 20))
charg = font.render("Chargement en cours ...", True, (255, 255, 255))
screen.blit(
    charg,
    (largeur // 2 - charg.get_width() // 2, hauteur // 2 - charg.get_height() // 2),
)
pygame.display.flip()


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

font = pygame.font.SysFont("Georgia", 15)
charg = font.render("CHARGEMENT PATIENTEZ QUELQUES SECONDES", True, NEIGE)
screen.blit(charg, (hauteur // 2, largeur // 2))
pygame.display.flip()


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

etait_monde = False
etait_onde = False
etait_sable = False
etait_foret = False
etait_plaine = False
etait_neige = False
etait_mer = False
etait_montagne = False

while running:
    events = pygame.event.get()
    set_events(
        events
    )  # On récupère les évènement qu'une fois dans la boucle car on avait besoin de les récupérer aussi dans la génération de maison sauf que si on fait get.event deux fois dans la même frame la deuxième fois qu'on l'appelle on récupère une liste vide car get vide la liste d'event.

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

            # Evenements de contrôles particuliers propres aux mondes ou pour passer au monde précédent avec la touche retour arrière
            if (monde or onde):
                if event.key == pygame.K_BACKSPACE:
                    onde = False
                    monde = False
                    lancement = True
            if sable or foret or plaine or neige or mer or montagne:
                if event.key == pygame.K_BACKSPACE:
                    sable = False
                    foret = False
                    plaine = False
                    neige = False
                    mer = False
                    montagne = False
                    if etait_monde:
                        monde = True
                    elif etait_onde:
                        onde = True
            if village:
                if event.key == pygame.K_BACKSPACE:
                    village = False
                    if etait_sable:
                        sable = True
                    if etait_foret:
                        foret = True
                    if etait_plaine:
                        plaine = True
                    if etait_neige:
                        neige = True
                    if etait_mer:
                        mer = True
                    if etait_montagne:
                        montagne = True

                if event.key == pygame.K_r:  # régénérer village
                    regenerer_village()
                    generate_village()
                    dessine_carte_village()
            if maison:
                if event.key == pygame.K_BACKSPACE:
                    maison = False
                    village = True
            if donjon:
                if event.key == pygame.K_BACKSPACE:
                    donjon = False
                    maison = True

                if event.key == pygame.K_r:  # touche R → régénère une nouvelle map
                    regenerer_donjon()

        # Evenements pour lancer le prochain monde en cliquant sur le bon élément
        if event.type == pygame.MOUSEBUTTONDOWN:
            if bouton_1.collidepoint(event.pos) and lancement:
                lancement = False
                monde = True
                etait_monde = True
                etait_onde = True
                genere_et_dessine_carte_monde()
            elif bouton_2.collidepoint(event.pos) and lancement:
                lancement = False
                onde = True
                etait_onde = True
                etait_monde = False
                genere_et_dessine_carte_onde(_nouvelle_grille())
            elif (monde or onde):  # On vérifie le clic sur la map seulement si on est dans un des deux mondes
                couleur_clic = screen.get_at(event.pos)[:3]
                if couleur_clic == SABLE:
                    monde = False
                    onde = False
                    sable = True
                    etait_sable = True

                    etait_foret = False
                    etait_plaine = False
                    etait_neige = False
                    etait_mer = False
                    etait_montagne = False

                    genere_et_dessine_carte_sable()
                if couleur_clic == FORET:
                    onde = False
                    monde = False
                    foret = True
                    etait_foret = True

                    etait_sable = False
                    etait_plaine = False
                    etait_neige = False
                    etait_mer = False
                    etait_montagne = False

                    genere_et_dessine_carte_foret()
                if couleur_clic == PLAINE:
                    onde = False
                    monde = False
                    plaine = True
                    etait_plaine = True

                    etait_sable = False
                    etait_foret = False
                    etait_neige = False
                    etait_mer = False
                    etait_montagne = False

                    genere_et_dessine_carte_plaine()
                if couleur_clic == NEIGE:
                    onde = False
                    monde = False
                    neige = True
                    etait_neige = True

                    etait_sable = False
                    etait_foret = False
                    etait_plaine = False
                    etait_mer = False
                    etait_montagne = False

                    genere_et_dessine_carte_neige()
                if couleur_clic == MER:
                    onde = False
                    monde = False
                    mer = True
                    etait_mer = True

                    etait_sable = False
                    etait_foret = False
                    etait_plaine = False
                    etait_neige = False
                    etait_montagne = False

                    genere_et_dessine_carte_mer()
                if couleur_clic == MONTAGNE:
                    onde = False
                    monde = False
                    montagne = True
                    etait_montagne = True

                    etait_sable = False
                    etait_foret = False
                    etait_plaine = False
                    etait_neige = False
                    etait_mer = False

                    genere_et_dessine_carte_montagne()
            elif sable or foret or plaine or neige or mer or montagne:
                couleur_clic = screen.get_at(event.pos)[:3]
                if couleur_clic in (VILLAGE, VILLAGE_M):
                    sable = False
                    foret = False
                    plaine = False
                    neige = False
                    mer = False
                    montagne = False
                    village = True
                    regenerer_village()
                    generate_village()
                    dessine_carte_village()

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
                    regenerer_donjon()
    pygame.display.flip()
pygame.quit()
