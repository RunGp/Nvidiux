# Nvidiux
Licence GPL3 https://github.com/RunGp/Nvidiux/blob/master/usr/share/nvidiux/gpl-3.0.txt

=============================================================

English version - (Description en Francais en bas de page)

Nvidiux is a graphical python tool to overclock or underclock your nvidia gpu (generation 4XX or newer)
also provide :
- Fan control 
- Auto overclock at startup
- Graphical monitoring for 4 params (temp,gpu load,speed fan (%) and graphic memory use (%))
- Overvolting

Work on : 
- Ubuntu 12.04+ and derivative 
- Debian 7.0+
- Arch and Manjaro
- Fedora 15+

For using this tools you must install 
 - Nvidia proprietary drivers 331 or later 
    - For use overclock drivers 337 or later
    - For use overvolt drivers 346 or later

Install 

Debian
in command line use :
- wget https://github.com/RunGp/Nvidiux/releases/download/2.1/nvidiux.deb
- sudo dpkg -i nvidiux.deb
- sudo apt-get install -f

Ubuntu 
use this ppa https://launchpad.net/~nvidiux/+archive/ubuntu/nvidiux or use the deb file in release

Arch - Manjaro
Nvidiux is available on AUR : https://aur.archlinux.org/packages/nvidiux/

Red Hat Family
Use rpm package here : https://github.com/RunGp/Nvidiux/releases or http://schotty.com/yum/el/7/repoview/nvidiux.html

Dependancy:python 2.7,python-qt4,gksu,vainfo,python-tk,python-psutil

![alt tag](http://pix.toile-libre.org/upload/original/1448449352.png)

=============================================================

I need help for traduce nvidiux in other language
Special thanks to
- @mglinux for german translation
- @profesorfalken for spanish translation
- @gaara @bishop @gfx @jul974 for testing and help for debug
- @andrewschott for packaging nvidiux (rpm package)

=============================================================

FR Version
Plus d'information : http://forum.ubuntu-fr.org/viewtopic.php?id=1589261

Nvidiux est un outil graphique pour overclocker/underclocker facilement votre gpu nvidia (generation 4XX ou plus recent)
Il permet aussi 
 
- d'overclocker au demarrage du programme et/ou du systeme
- controller la vitesse des ventilos du gpu
- monitorer 4 parametres (temperatures , charge gpu et mémoire,vitesse ventillo)
- overvoltage

Pour installer vous devez installer :
  - Les pilotes nvidia propriétaire version 331 ou plus recent 
    - Pour utiliser l'overclock vous devez avoir la version 337 au minimum
    - Pour utiliser l'overvolt vous devez avoir la version 346 au minimum
  
Testé sous:
- Ubuntu 12.04 + et ses dérivés
- Debian 7.0 +
- Arch et Manjaro
- Fedora 15 +
  
Installation :

Debian
Installez le paquet deb se trouvant ici (https://github.com/RunGp/Nvidiux/releases) avec votre instalateur de paquet favoris
Ou taper les commandes dans votre terminal:
- wget https://github.com/RunGp/Nvidiux/releases/download/2.1/nvidiux.deb
- sudo dpkg -i nvidiux.deb
- sudo apt-get install -f

Ubuntu
Un ppa est dispo : https://launchpad.net/~nvidiux/+archive/ubuntu/nvidiux vous pouvez aussi utiliser le fichier deb dans les release

Arch - Manjaro
Nvidiux est disponible sur AUR : https://aur.archlinux.org/packages/nvidiux/

Red Hat et derivé
Utilisez le paquet rpm se trouvant ici : https://github.com/RunGp/Nvidiux/releases ou http://schotty.com/yum/el/7/repoview/nvidiux.html

Dependance:python 2.7,python-qt4,gksu,vainfo,python-tk,python-psutil

![alt tag](http://pix.toile-libre.org/upload/original/1448449268.png)

=============================================================

