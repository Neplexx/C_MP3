import yt_dlp, re, requests, os, sys, threading
from mutagen.id3 import ID3, TPE1, TALB, TIT2, APIC #la petite "*" vous pouvez vous la mettre dans le cul hehe
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QLineEdit

#pyinstaller --noconsole ConvertisseurMP3.py
#dédicace à ma variable backslash qu'elle repose en paix

class PrincipalWindow(QWidget): #chiantos mais au moins je peux utiliser 100% de QWidget et si vous voulez une explication de qu'est qu'une classe allez voir sur google
    def __init__(self):         #pareil un peu chiantos mais c'est ce qui permet de tout appeler lors de la création d'une interface graphique en Qt et c'est aussi le "start" d'une classe
        super().__init__()      #(en gros vérifie que QWidget à bien était lancé correctement)
        self.execute()          

    def execute(self):           #fonction des paramètres de base de la fenetre 
        self.resize(1920, 1080)
        self.move(0,0)           #un peu con mais par défaut c'est pas bien centré
        self.setWindowTitle("Convertisseur mp3") 

        icone = QIcon(r"C:\Users\detal\Desktop\V , M , P\MONTAGE PS § ILL\logo\cadena.jpg") #au cas où vous savez pas sales incultes le "r" permet de ne pas prendre en compte les merdes comme "\" qui seront considérés comme des caractères "basique"
        self.setWindowIcon(icone)

        self.Interface()           #je précise : les "self" permettent de dire que cet élément fait partie de la class , et donc je peux l'utiliser partout , c'est en quelques sortes attribué à la classe ce qui me permet d'utiliser les paramètres de celle-ci (ici QWidget)
        self.show()                

    def Interface(self):           #fonction des paramètres graphiques de la fenetre (genre tel boutton va là etc)

        fond = QLabel(self)                                          #affichage d'une couleure ici comme fond
        fond.setStyleSheet("background-color: lightgray;")
        fond.resize(1920, 1080)

        self.URLS = QLineEdit(self)                                 #attribue à la variable URLS ce que l'utilisateur rentre dans la ligne (utilisation de self ici car j'ai besoin qu'il soit attribué comme paramètre de la fonction pour pouvoir le réutiliser plus tard)
        self.URLS.setFixedSize(400, 30)                              #tous les paramètres de tailles etc (en gros aller voir un guide sur le QT si vous voulez comprendre chaque paramètre)
        self.URLS.setStyleSheet("QLineEdit { border-radius : 2px ; border : 1px solid black ; }")
        self.URLS.move(750, 500)

        txt_URLS = QLabel(self)                          #affichage d'un petit texte
        txt_URLS.setText("Lien vers la musique :")
        txt_URLS_font = QFont("Arial", 12)
        txt_URLS.setFont(txt_URLS_font)
        txt_URLS.move(850, 430)

        download_button = QPushButton(self)              #affichage d'un boutton avec tous ses paramètres
        download_button.setFixedSize(100, 40)
        download_button.setStyleSheet("QPushButton { border: 1px solid black; }QPushButton:pressed {background-color: lightgray;}")
        download_button.setText("Télécharger")
        download_button_font = QFont("Arial", 8)
        download_button.setFont(download_button_font)
        download_button.move(890, 600)
        download_button.clicked.connect(self.start_download)          #c'est ce qui permet d'éxecuter une fonction quand tu appuies sur le bouton

        self.téléchargement = QLabel(self)  
        self.téléchargement.setText("Téléchargement en cours")
        self.téléchargement_font = QFont("Arial", 12)
        self.téléchargement.setFont(self.téléchargement_font)
        self.téléchargement.move(850, 740)
        self.téléchargement.setVisible(False)

    def start_download(self):
        chemin = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de sauvegarde") #fenetre qui s'ouvre permettant d'indiquer le chemin (merci Qt qui a ce paramètre par défaut)
        URLS = self.URLS.text()

        self.téléchargement.setVisible(True)

        download_thread = threading.Thread(target=self.ConvertisseurMP3, args=(URLS, chemin))  #permet un téléchargement séparé de l'interface empechant un freeze de l'interface (encore merci Qt qui a un paramètre fait exprès pour ça)
        download_thread.start()                                                                #et si vous voulez comprendre chaque truc Qt aller voir leur documentation , tout y est expliqué

    def ConvertisseurMP3(self, URLS, chemin): #la fonction permettant la conversion etc...
        
        ydl_opts = {                                           #bon concrètement c'est les options de téléchargements présent dans la bibliothèque ydl  
                                                               #amusez vous bien : https://github.com/yt-dlp/yt-dlp/blob/master/README.md
            'outtmpl': chemin + "\\" + r"%(title)s.%(ext)s",     #permet d'indiquer le chemin d'accès vers le téléchargement avec l'utilisation d'espaces qui seront changer lors du téléchargement par leurs vrais valeurs
            'format': 'bestaudio/best',                          #paramètre qui dit concrètement "prend la meilleure qualité disponible sur la partie audio de la vidéo"
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',                      #paramètre d'après téléchargement utilisant ffmpeg
                'preferredcodec': 'mp3',                         
            }],
        }

                                                                   
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_trouve = ydl.extract_info(URLS, download=False)      #c'est ce qui va chercher toutes les infos à partir de l'url et empecher le téléchargement de la vidéo , seulement l'audio
            ydl.download([URLS])                                    #téléchargement de l'audio 
            musique_nom = info_trouve.get('title', 'inconnu')         #le paramètre est imple : si il trouve l'info il le met en titre , sinon il met inconnu
            musique_auteur = info_trouve.get('uploader', 'inconnu')

        if 'album' in info_trouve:                                     #meme principe mais cette fois en remplaçant par musique_nom
            musique_album = info_trouve['album']
        else:
            musique_album = musique_nom


        image_test = requests.get(URLS)                             #bibliothèque qui permet d'envoyer une demande à partir d'un lien(ici je l'utilise pour récupérer et télécharger l'image)
        if image_test.status_code == 200:                            #(200 est une sorte d'équivalent de True dans cette bilio)
            image_url = image_test.text.split('<meta property="og:image" content="')[1].split('"')[0]  #va chercher l'url de l'image à partir de celle de la vidéo (amusez vous bien avec toute la documentation : https://requests.readthedocs.io/en/latest/)
            image = requests.get(image_url) #télécharger l'image
            if image.status_code == 200:
                with open(chemin + "\\" + self.Nettoie(info_trouve['title']) + ".jpg", "wb") as image_finale: #l'envoie au meme endroit que le fichier mp3 avec le meme nom pour simplifier le tout
                    image_finale.write(image.content)


        fichier_mp3 = chemin + "\\" + self.Nettoie(info_trouve['title']) + '.mp3'    #défini les 2 fichiers à partir de leurs emplacements
        image_mp3 = chemin + "\\" + self.Nettoie(info_trouve['title']) + '.jpg'

        with open(image_mp3, 'rb') as image_finale:     ##bon ici en gros j'utilise mutagen pour modifier les valeurs du fichier (auteur , albums ,etc..) : https://mutagen.readthedocs.io/en/latest/user/id3.html
            image_bidule = image_finale.read()

        audio = ID3(fichier_mp3)                        
        audio.add(TIT2(encoding=3, text=musique_nom))   #concrètement tu encodes la valeur que tu veux
        audio.add(TPE1(encoding=3, text=musique_auteur))
        audio.add(TALB(encoding=3, text=musique_album))

        yeah = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=image_bidule)
        audio.add(yeah)
        audio.save()

        os.remove(chemin + "\\" + self.Nettoie(info_trouve['title']) + '.jpg')  #delete l'image attribué au fichier une fois que tout est fini

        self.téléchargement.setVisible(False)


    def Nettoie(self, texte):               #permet de me dégager les merdes en les remplaçant par un "_" parce que autrement lors du téléchargement le chemin est pas compris
        return re.sub(r'[\/:*?"<>|]', '_', texte)     # et pourquoi galérer quand une bibliothèque te le fait tout seul
            

def main():
    application = QApplication(sys.argv)     #me sers pour la ligne juste après mais en gros c'est ce qui permettre de créer la fenetre
    fenetre = PrincipalWindow()               #permet d'appeler en fenetre la classe principale (va avec le .show dans la fonction execute)
    sys.exit(application.exec_())            #permet d'ouvrir et de fermer la fenetre sans tous faire bug/crash

if __name__ == '__main__':                  #permet de lancer automatiquement main() au démarrage du programme  (en vrai j'ai compris pourquoi on utilise ça en Qt c'est stylé pour éviter des confusions quand tu importes un programme)
    main()
