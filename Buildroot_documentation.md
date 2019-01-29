## Buildroot_documentation.md
***************************************
**Cette partie se passe dans le docker.**

Tout d'abord, téléchargez l'image Docker suivante:

````
$ docker pull pblottiere/embsys-rpi3-buildroot
````

Ensuite, créez un conteneur à partir de cette image:

````
$ docker run -it pblottiere/embsys-rpi3-buildroot /bin/bash
````

Décompressez la tarball et placez-vous dans ce docker:


````
# tar zxvf buildroot-precompiled-2017.08.tar.gz
# cd buildroot-precompiled-2017.08
````

## Comment utiliser buildroot
**Cette partie se passe dans le docker.**

Afin d'obtenir la version de buildroot compilée pour l'architecture voulue, lancer la commande:

```
# make embsys_defconfig
```


Maintenant, lancez la commande suivante pour afficher le menu de configuration:

````
# make menuconfig
````

Après avoir utilisé cette commande et avoir fait "Save", la configuration de compilation sera sauvegardée dans "/root/buildroot-precompiled-2017.08/.config"

Pour notre projet, il nous faudra les modules suivants:

**en C:**

    - stdio
    - sdtlib
    - string
    - assert
    - getopt
    - fcntl
    - unistd
    - errno
    - malloc
    - sys/*
    - time
    - asm/types
    - linux/videodev2
    - jpeglib
    - libv4l2
    - signal
    - stdint
    - inttypes

**en Python:**
    
    - socket
    - tkinter
    - matplotlib
    - sys
    - os 
    - gpio 


Pour valider la compilation et obtenir notre toolchain, il faut maintenant lancer la commande:

````
# make toolchain
````

Si nécessaire, on pourrait modifier les options de build avec la busybox via la commande:


````
# make busybox
````

Puis pour obtenir notre architecture compilée, on appelle la commande:


````
# make
````

Le résultat de la compilation est alors une image du kernel ainsi que le bootloader et un RFS (notamment).

***************************************

## Comment flasher la carte

***************************************