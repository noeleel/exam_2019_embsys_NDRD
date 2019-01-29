## Buildroot_documentation.md
***************************************
**Cette partie se passe dans le docker.**

Tout d'abord, téléchargez l'image Docker suivante:

```` shell
$ docker pull pblottiere/embsys-rpi3-buildroot
````

Ensuite, créez un conteneur à partir de cette image:

```` shell
$ docker run -it pblottiere/embsys-rpi3-buildroot /bin/bash
````

Décompressez la tarball et placez-vous dans ce docker:


```` shell
# tar zxvf buildroot-precompiled-2017.08.tar.gz
# cd buildroot-precompiled-2017.08
````

## Comment utiliser buildroot
**Cette partie se passe dans le docker.**

Afin d'obtenir la version de buildroot compilée pour l'architecture voulue, lancer la commande:

``` shell
# make embsys_defconfig
```


Maintenant, lancez la commande suivante pour afficher le menu de configuration:

```` shell
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


Pour valider la compilation et obtenir notre toolchain de cross-compilation, il faut maintenant lancer la commande:

```` shell
# make toolchain
````

Si nécessaire, on pourrait modifier les options de build avec la busybox via la commande:


```` shell
# make busybox
````

Une fois correctement configuré, il suffit de lancer la compilation avec la
commande *make*. Le résultat de la compilation est alors une image du kernel
ainsi que le bootloader et un RFS (notamment).

On peut alors copier cette ce bootloader et ce RFS sur notre ordinateur hôte. On lance alors :

```` shell
# mkdir /tmp/rootfs
# tar -xf output/images/rootfs.tar -C /tmp/rootfs
````

Puis on récupère toute l'arborescence du dossier rootfs sur notre ordinateur hôte via un "docker cp". 

```` shell
$ docker cp <container_id>:/tmp/rootfs/ .
````

***************************************

## Comment flasher la carte

Tout d'abord récupérer l'image complet de la carte SD du conteneur Docker sur
votre machine hôte:

```` shell
$ docker cp <container_id>:/root/buildroot-precompiled-2017.08/output/images/sdcard.img .
````

Ensuite, sur une carte SD disponible à travers */dev/sdX* (remplacer *X* par le
path de votre carte. *dmesg* peut vous aider):

```` shell
$ sudo dd if=sdcard.img of=/dev/sdX
````


Ensuite, branchez l'adaptateur USB-TTL sur les ports TX/RX et ouvrez un
terminal série (gtkterm, minicom, ...). Finalement, connectez vous au réseau
avec un cable Ethernet, insérez la carte SD et démarrez la RPI3.

Pour vous connecter en *user*:

    Login: user
    MdP: user1* 

Pour vous connecter en *root*:

    Login: root
    MdP: root1* 
***************************************