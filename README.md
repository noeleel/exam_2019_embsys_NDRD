# exam_2019_embsys_NDRD

Repository git pour le projet embsys, fait par DO ROSARIO Maxime, DELMAS Sarah, NOELE Elodie. 

*****************************************

## Livrables attendus

Livrables:

- dépôt Github dédié à votre projet
- le code
- README exhaustif (comment utiliser Buildroot, flasher la carte, compiler et
  installer votre outil, documentation utilisateur, etc)

Critères de notation:

- Produit fonctionnel
- Architecture du code et modularité (librairies, ...)
- Outils de build (autotools, CMake ou Makefile)
- Utilisation des notions vues en TP (getopt, syslog, signal handler, ...)
- Normes de codage

//!\\ Pensez aux signaux handlers, etc ... 

*****************************************
## Dans Buildroot_documentation.md
    Vous trouverez:

        Comment utiliser buildroot

        Comment flasher la carte

*****************************************

## Documentation utilisateur

## Serveur servomoteur

## Client

## Serveur caméra

*****************************************

**Répartition des tâches**:
    
    Elodie:
        1) Cross-compilation de la carte RPi avec Buildroot.
        2) Serveur servomoteur (Python) afin de contrôler le servomoteur via la RPi3. Utilisation d'une pin GPIO en mode PWM. (cf TP embsys)

    Maxime:
        Client (Python) avec interface graphique sous Tkinter + matplotlib
    
    Sarah:
        Serveur caméra(C), contrôle de la caméria via la RPI3 avec l'API C V4L.

**Etat d'avancement**