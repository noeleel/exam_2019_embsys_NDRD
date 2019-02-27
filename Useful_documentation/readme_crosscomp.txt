utilisation d'un code pour prendre une image du flux camera (https://github.com/twam/v4l2grab)

crosscompiler par buildroot dans docker
options de compilation dans  https://www.gnu.org/software/autoconf/manual/autoconf-2.69/html_node/Hosts-and-Cross_002dCompilation.html

Après crosscompilation executer :
rpi3# ./v4l2grab -d /dev/video0 -o image.jpg
et verifier image.jpg

modifier le code v4l2grab.c

###

télécharger et dezipper image docker:

$ sudo docker rmi pblottiere/embsys-rpi3-buildroot-video
$ sudo docker pull pblottiere/embsys-rpi3-buildroot-video
$ sudo docker run -it pblottiere/embsys-rpi3-buildroot-video /bin/bash
# cd /root/
# tar zxvf buildroot-precompiled-2017.08.tar.gz
apt update
apt upgrade
apt install nano //pour pouvoir editer .c


pour cross compil:
telecharger https://github.com/twam/v4l2grab
ds v4l2grab-master (https://github.com/twam/v4l2grab/wiki/Installation)
copier fichiers ds docker /root:
sudo docker ps //donne nom_du_docker
sudo docker cp v4l2grab-master nom_du_docker:/root/

./autogen.sh //create autotool files
./configure CC=~/buildroot-precompiled-2017.08/output/host/usr/bin/arm-linux-gcc --host=arm-buildroot-linux-uclibcgnueabihf --build=linux //run configure --build pas obligatoire
make
//erreur dans make, undefined reference to `rpl_malloc'
modifier config.h
mettre #define HAVE_MALLOC 0 à #define HAVE_MALLOC 1
et commenter #define malloc rpl_malloc

make install


copier binaire v4l2grab sur rpi3 (ici git)
sudo docker cp nom_du_docker:/root/v4l2grab-master/v4l2grab 

sudo docker cp eager_brattain:/root/v4l2grab-master/v4l2grab

Dans le cadre d'un projet utilisant les autotools, le fichier *.gitignore*
contiendra ceci:

```` bash
v4l2grab-master/Makefile.in
v4l2grab-master/aclocal.m4
v4l2grab-master/autom4te.cache/
v4l2grab-master/config.h.in
v4l2grab-master/config/
v4l2grab-master/configure
v4l2grab-master/Makefile
v4l2grab-master/config.h
v4l2grab-master/config.status
v4l2grab-master/libtool
v4l2grab-master/m4/
v4l2grab-master/stamp-h1
v4l2grab-master/.deps
v4l2grab-master/.dirstamp/
````
qd recoit 1 du client, envoit image
si 0 envoit rien

