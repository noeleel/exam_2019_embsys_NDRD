# exam_2019_embsys_NDRD

Repository git pour le projet embsys, fait par DO ROSARIO Maxime, DELMAS Sarah, NOELE Elodie. 


*****************************************
## Dans Buildroot_documentation.md

**Cette partie se passe dans le docker.**

Tout d'abord, téléchargez l'image Docker suivante:

```` shell
$ docker pull pblottiere/embsys-rpi3-buildroot-video
````

Ensuite, créez un conteneur à partir de cette image:

```` shell
$ docker run -it pblottiere/embsys-rpi3-buildroot-video /bin/bash
````

Décompressez la tarball et placez-vous dans ce docker:


```` shell
# tar zxvf buildroot-precompiled-2017.08.tar.gz
# cd buildroot-precompiled-2017.08
````

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
Le nécessaire pour flasher la carte RPI3 avec le support de la caméra est
alors disponible:

- `sdcard.img` à flasher sur la carte SD avec la commande `dd`
- `start_x.elf` et `fixup_x.dat` à copier avec la commande `cp` sur la 1ère
partition de la carte SD. A trouver dans "/root/buildroot-precompiled-2017.08/output/build/rpi-firmware-685b3ceb0a6d6d6da7b028ee409850e83fb7ede7/boot"s

Il faut finalement modifier le fichier `config.txt` de la 1ère partition
de la carte SD pour ajouter:

````
start_x=1
gpu_mem=128
````

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

Pour vous connecter en *root*:

    Login: root
    MdP: root1* 

A chaque démarrage de la RPi, lancer la commande :
```` shell
$ modprobe bcm2835-v4l2
````
## Compilation du serveur caméra

    Pour mettre en place le serveur caméra, nous avons utilisé et modifié le code de : 
    https://github.com/twam/v4l2grab.  Les options de compilation sont spécifiées ici : https://www.gnu.org/software/autoconf/manual/autoconf-2.69/html_node/Hosts-and-Cross_002dCompilation.html.
    La compilation se fera exclusivement dans le docker utilisé par buildroot.

    Après modification du code, on met en place le docker:

```` shell
$ sudo docker rmi pblottiere/embsys-rpi3-buildroot-video
$ sudo docker pull pblottiere/embsys-rpi3-buildroot-video
$ sudo docker run -it pblottiere/embsys-rpi3-buildroot-video /bin/bash
# cd /root/
# tar zxvf buildroot-precompiled-2017.08.tar.gz
# apt update
# apt upgrade
# apt install nano
````

    Pour la cross-compilation, on copie les fichiers de v4l2grab-master dans le docker avec la commande suivante: (en cas d'erreur dans le make, modifier le fichier config.h et mettre #define HAVE_MALLOC 0 à #define HAVE_MALLOC 1 et commenter #define malloc rpl_malloc)
    
```` shell
$ sudo docker cp v4l2grab-master <container_id>:/root/ .
$ cd v4l2grab-master
$ ./autogen.sh
$ ./configure CC=~/buildroot-precompiled-2017.08/output/host/usr/bin/arm-linux-gcc --host=arm-buildroot-linux-uclibcgnueabihf --build=linux 
$ make
$ make install
````

    Après cross-compilation, on peut récupérer le binaire pour le mettre sur la carte SD. Après s'être placé sur le dossier /home/user de la RPi:
        ```` shell
        $ sudo docker cp <container_id>:/root/v4l2grab-master/v4l2grab .
        ````

## Fonctionnement de l'ensemble de l'application

    Le serveur client fonctionne sous Python3.6 (pour Tkinter).
    Le serveur caméra fonctionne en C.
    Le serveur servomoteur fonctionne sous Python2.7 (pour la Raspberry).

    Le serveur client est chargé de gérer à la fois le serveur caméra et le serveur servomoteur à travers le runtime. Au bout de 10 tentatives de connexions infructueuses avec l'un des deux, le serveur client s'arrête. 

    Le serveur servomoteur gère le servomoteur au moyen du PWM. Il reçoit la commande en angle du serveur client en bytes qu'il convertit en degrés. Ce serveur s'arrête dès que le client se déconnecte ou qu'aucun client ne s'est connecté en l'espace de 5 minutes.

    Le serveur caméra prend des photographies via la librarie libv4l2. Il les envoie ensuite par
    paquets réguliers, toutes les 40 ms, au serveur client lorsqu'il reçoit la commande. 
    Pour arrêter ce serveur, il faut lui envoyer un signal SIGKILL. 

    Pour chaque photographie prise, celle-ci s'affichera dans l'interface graphique Tkinter. 

*****************************************

## Documentation utilisateur

    Pour lancer le programme, sur la RPi :

        python Servomotor_server.py & ./v4l2grab -d /dev/video0

    Cette commande lance le serveur du servomoteur sur l'adresse "192.168.1.20:9000" 
    et le serveur de la caméra sur l'adresse "192.168.1.20:7000".

    Sur l'ordinateur client :
    
        python3.6 Client.py

## Serveur servomoteur

    Pour lancer le serveur servomoteur, sur la RPi, il faut lancer la commande suivante:
        python Servomotor_server.py.
    
    Il est possible de configurer le serveur avec les options suivantes (qui sont affichables avec
    l'option '-h' ou '--help'):

        -g or --gpio_pin        | Required. Board pin of the RPi to which the servomotor pin control will be attached
        -i or --ip              | Default is localhost. Ip Address of the RPi on which the server is running. 
        -p or --port            | Default is 9000. Port of the RPi on which the server is running
        -b or --buffer_size     | Default is 1024. Buffer size in bytes for receiving the command data for the client
        -t or --timeout         | Default is 300. Time in seconds before the server will end. 

## Client

    La capture d'image se passe sous la forme d'une vidéo/diaporama (de l'ordre de l'image par secondes)


    ![image](Client_image.png)

        1 -  Barre pour la position du servomoteur 
        2 -  Bouton Capture/Stop permettant de lancer ou arreter la capture
        3 - Bouton pour quitter l'application
        4 - Fenêtre d'affichage de la vidéo/image, l'image est de 640*480 et en gris
        5 - Indicateur de la connexion entre la Caméra et le Client (Vert ok / Rouge caméra non connectée)
        6 -  Indicateur de la connexion entre le Servomoteur et le Client (Vert ok / Rouge servomoteur non connecté)

    Il est possible de configurer le client avec les options suivantes (qui sont affichables avec
    l'option '-h' ou '--help'):

        -i or --ip               | Default is localhost. Ip Address of the RPi on which the server is running.
        -s or --port_servomoteur | Default is 9000. Port of the RPi on which the server managing the servomotor is running.
        -c or --port_camera      | Default is 7000. Port of the RPi on which the server managing the camera is running.
            
## Serveur caméra

    Le serveur caméra se lance avec la commande ./v4l2grab -d /dev/video0. Le serveur caméra est configurable avec les options suivantes (affichables aussi avec la commande '-h' ou '--help')

		-p or --port		  | RPi Port on which the camera server will be launched
		-d or --device name   | Video device name [/dev/video0]
		-v or --version       | Print version

*****************************************

## Modification de l'IP de la Raspberry

    L'adresse Ip de la carte Raspberry a été configurée de manière statique sur l'IP "192.168.1.20".
    Si cette Ip n'appartient à votre réseau ou est déjà utilisé, vous pouvez la modifier en modifiant le
    fichier /etc/network/interfaces dans le système de fichiers de la RPi situé sur la carte SD. 

    Afin de configurer l'ip de manière statique, remplacez les lignes de votre fichier par celles-ci :

        auto lo
        iface lo inet loopback

        auto eth0
        iface eth0 inet static
                address 192.168.1.20
                network 192.168.1.0
                netmask 255.255.255.0