# Nvidiux beta version 0.97
En version
Nvidiux is a graphical python tool to overclock or underclock your nvidia gpu  (generation 4XX  5XX  6XX 7XX)
il also provide :
- fan control 
- Auto overclock at startup
- Graphical monitoring for 4 params (temp,gpu load,speed fan (%)graphic memory use (%))

![alt tag](http://pix.toile-libre.org/upload/original/1438594970.png)

![alt tag](http://pix.toile-libre.org/upload/original/1438596113.png)

For using this tools you must install 
 - nvidia proprietary drivers 331 or later (min 337 to use overclock)

simply install the deb file here : https://github.com/RunGp/Nvidiux/releases with your package manager
or in command line use

wget https://github.com/RunGp/Nvidiux/releases/download/0.97/nvidiux.deb
sudo dpkg -i nvidiux.deb
sudo apt-get install -f (for dependancy:,python 2.7,python-qt4,gksu,vainfo,python-tk,python-psutil)
and launch nvidiux

Work on ubuntu 12.04+ and derivative 

debian 7.0+

arch (manual installation dependancy:python 2.7,python-qt4,gksu,vainfo,python-tk,python2-psutil)

FR Version
Plus d'information (Francais) : http://forum.ubuntu-fr.org/viewtopic.php?id=1589261

Nvidiux est un outil graphique pour overclocker/underclocker facilement votre gpu nvidia (generation 4XX ou plus recent)
Il permet aussi 
 
- d'overclocker au demarrage du programme et/ou du systeme
- controller la vitesse des ventilos du gpu
- monitorer 4 parametres (temperatures , charge gpu et mémoire,vitesse ventillo)

Pour installer vous devez installer :
  - Les pilotes nvidia propriétaire version 331 ou mieux ( pour utiliser l'overclock vous devez avoir la version 337 au minimum)
Installation :
	Installez le paquet deb se trouvant ici (https://github.com/RunGp/Nvidiux/releases) avec la logitheque
	
ou taper les commandes dans votre terminal:

wget https://github.com/RunGp/Nvidiux/releases/download/0.97/nvidiux.deb
sudo dpkg -i nvidiux.deb
sudo apt-get install -f (for dependancy:,python 2.7,python-qt4,gksu,vainfo,python-tk,python-psutil)

testé sous
Ubuntu 12.04 +
debian 7.0 +
Arch
Fedora 15

=============================================================
Licence:gpl-3.0 :https://github.com/RunGp/Nvidiux/blob/master/usr/share/nvidiux/gpl-3.0.txt




