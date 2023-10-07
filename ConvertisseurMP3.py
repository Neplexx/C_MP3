import yt_dlp, re, requests, os, sys, threading
from mutagen.id3 import ID3, TPE1, TALB, TIT2, APIC #la petite "*" vous pouvez vous la mettre dans le cul hehe
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt , QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QLineEdit, QFrame , QMenuBar, QProgressBar

#From Neplexx's Inc 
#pyinstaller --noconsole ConvertisseurMP3.py
#auto-py-to-exe
#dédicace à ma variable backslash qu'elle repose en paix

class PrincipalWindow(QWidget): #chiantos mais au moins je peux utiliser 100% de QWidget et si vous voulez une explication de qu'est qu'une classe allez voir sur google
    def __init__(self):         #pareil un peu chiantos mais c'est ce qui permet de tout appeler lors de la création d'une interface graphique en Qt et c'est aussi le "start" d'une classe
        super().__init__()
        self.execute()          

    def execute(self):           #fonction des paramètres de base de la fenetre 
        self.resize(1920, 1080)
        self.move(0,0)           #un peu con mais par défaut c'est pas bien centré
        self.setWindowTitle("Convertisseur mp3") 

        icone = QIcon(r"C:\Users\detal\Desktop\V , M , P\MONTAGE PS § ILL\logo\cadena.jpg") #au cas où vous savez pas sales incultes le "r" permet de ne pas prendre en compte les merdes comme "\" qui seront considérés comme des caractères "basique"
        self.setWindowIcon(icone)

        self.Interface()           
        self.show()                

    def Interface(self):           #fonction des paramètres graphiques de la fenetre (genre tel boutton va là etc)
        fond = QLabel(self)                                          
        fond.setStyleSheet("background-color: #212121;")
        fond.resize(1920, 1080)

        fond2 = QFrame(self)
        fond2.setFixedSize(1600,900)
        centré_horizontalement_fond2 = (self.width()-fond2.width())//2
        centré_verticalement_fond2 = (self.height()-fond2.height())//2 - 28  #merci la barre des taches d'etre présente et de m'avoir fait galérer à centrer
        fond2.move(centré_horizontalement_fond2,centré_verticalement_fond2)
        fond2.setStyleSheet("background-color: #2c2c2c ; border-radius : 20px")

        self.URLS = QLineEdit(self)                                 #attribue à la variable URLS ce que l'utilisateur rentre dans la ligne
        self.URLS.setFixedSize(400,30)
        self.URLS.setStyleSheet("QLineEdit { border-radius : 2px ; border : 1px solid gray ; background-color:#2c2c2c ; color:lightgray }")
        centré_horizontalement_URLS = (self.width()-self.URLS.width())//2
        self.URLS.move(centré_horizontalement_URLS,500)

        txt_URLS = QLabel(self)                          #affichage d'un petit texte
        txt_URLS.setText("Lien vers la musique :")
        txt_URLS_font = QFont("Arial", 20)
        txt_URLS_font.setBold(True)
        txt_URLS.setFont(txt_URLS_font)
        txt_URLS.setStyleSheet("color:lightgray")
        txt_URLS.setFixedSize(290,60)
        centré_horizontalement_URLS_txt = (self.width()-txt_URLS.width())//2
        txt_URLS.move(centré_horizontalement_URLS_txt, 370)

        download_button = QPushButton(self)              #affichage d'un boutton avec tous ses paramètres
        download_button.setStyleSheet("QPushButton { border-radius : 5px ; border: 1px #1f528d ; background-color: #1f528d ; color:lightgray }")
        download_button.setText("Télécharger")
        download_button_font = QFont("Arial", 12)
        download_button.setFixedSize(200,40)
        download_button.setFont(download_button_font)
        centré_horizontalement_boutton = (self.width() - download_button.width())// 2 
        download_button.move(centré_horizontalement_boutton, 600)      # Centrer horizontalement le bouton ( 600 = hauteur et 100/40 sont les dimensions du button)
        download_button.clicked.connect(self.start_download)          #c'est ce qui permet d'éxecuter une fonction quand tu appuies sur le bouton

        self.téléchargement = QLabel(self)  
        self.téléchargement.setText("Téléchargement en cours...")
        self.téléchargement_font = QFont("Arial",20, italic=True)
        self.téléchargement.setFont(self.téléchargement_font)
        self.téléchargement.setStyleSheet("color:lightgray;")
        self.téléchargement.setFixedSize(330,60)
        centré_horizontalement_télécharement = (self.width()- self.téléchargement.width())//2
        self.téléchargement.move(centré_horizontalement_télécharement, 740)
        self.téléchargement.setVisible(False)

        self.progress_barre = QProgressBar(self)
        self.progress_barre.setFixedSize(250,30)
        self.progress_barre.setStyleSheet("QProgressBar {background-color: #2c2c2c;border-radius: 5px; border: 1px solid lightgray;} QProgressBar::chunk {background-color: lightgray;}") #j'aime pas le syntaxe type CSS
        centré_horizontalement_barre = (self.width()-self.progress_barre.width())//2
        self.progress_barre.move(centré_horizontalement_barre,820)
        self.progress_barre.setValue(0)
        self.progress_barre.setTextVisible(False)
        self.progress_barre.setVisible(False)
        

        #menuBar = QMenuBar(self)
        #menuBar.setGeometry(0,0, 500, 25)
        #File = menuBar.addMenu('File')
        #File.addAction("Fermer",exit)

    def start_download(self):
        chemin = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de sauvegarde") #fenetre qui s'ouvre permettant d'indiquer le chemin
        URLS = self.URLS.text()

        self.téléchargement.setVisible(True)
        self.progress_barre.setVisible(True)

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

        self.progress_barre.setValue(25)  

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_trouve = ydl.extract_info(URLS, download=False)      #c'est ce qui va chercher toutes les infos à partir de l'url et empecher le téléchargement de la vidéo , seulement l'audio
            ydl.download([URLS])                                      #téléchargement de l'audio 
            musique_nom = info_trouve.get('title', 'inconnu')         #le paramètre est imple : si il trouve l'info il le met en titre , sinon il met inconnu
            musique_auteur = info_trouve.get('uploader', 'inconnu')
        self.progress_barre.setValue(50)
        if 'album' in info_trouve:                                     #meme principe mais cette fois en remplaçant par musique_nom
            musique_album = info_trouve['album']
        else:
            musique_album = musique_nom

        self.progress_barre.setValue(75)
        image_test = requests.get(URLS)                             #bibliothèque qui permet d'envoyer une demande à partir d'un lien(ici je l'utilise pour récupérer et télécharger l'image)
        if image_test.status_code == 200:                            #(200 est une sorte d'équivalent de True dans cette bilio)
            image_url = image_test.text.split('<meta property="og:image" content="')[1].split('"')[0]  #va chercher l'url de l'image à partir de celle de la vidéo (amusez vous bien avec toute la documentation : https://requests.readthedocs.io/en/latest/)
            image = requests.get(image_url) #télécharger l'image
            if image.status_code == 200:
                with open(chemin + "\\" + self.Nettoie(info_trouve['title']) + ".jpg", "wb") as image_finale: #l'envoie au meme endroit que le fichier mp3 avec le meme nom pour simplifier le tout
                    image_finale.write(image.content)
            else:
                pass
        else:
            pass


        fichier_mp3 = chemin + "\\" + self.Nettoie(info_trouve['title']) + '.mp3'    #défini les 2 fichiers à partir de leurs emplacements
        image_mp3 = chemin + "\\" + self.Nettoie(info_trouve['title']) + '.jpg'


        with open(image_mp3, 'rb') as image_finale:     ##bon ici en gros j'utilise mutagen pour modifier les valeurs du fichier (auteur , albums ,etc..) : https://mutagen.readthedocs.io/en/latest/user/id3.html
            image_bidule = image_finale.read()

        audio = ID3(fichier_mp3)                        
        audio.add(TIT2(encoding=3, text=musique_nom))   #concrètement tu encodes la valeur que tu veux
        audio.add(TPE1(encoding=3, text=musique_auteur))
        audio.add(TALB(encoding=3, text=musique_album))

        self.progress_barre.setValue(90)

        yeah = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=image_bidule)
        audio.add(yeah)
        audio.save()

        os.remove(chemin + "\\" + self.Nettoie(info_trouve['title']) + '.jpg')  #delete l'image attribué au fichier une fois que tout est fini

        self.progress_barre.setValue(100)

        self.téléchargement.setVisible(False)
        self.progress_barre.setVisible(False)


    def Nettoie(self, texte):               #permet de me dégager les merdes en les remplaçant par un "_" parce que autrement lors du téléchargement le chemin est pas compris
        return re.sub(r'[\/:*?"<>|]', '_', texte)     # et pourquoi galérer quand une bibliothèque te le fait tout seul
            

def main():
    application = QApplication(sys.argv)     #me sers pour la ligne juste après mais en gros c'est ce qui permettre de créer la fenetre
    fenetre = PrincipalWindow()              #permet d'appeler en fenetre la classe principale (va avec le .show dans la fonction execute)
    sys.exit(application.exec_())            #permet d'ouvrir et de fermer la fenetre sans tous faire bug/crash

if __name__ == '__main__':                  #permet de lancer automatiquement main() au démarrage du programme si le code vient bien d'ici
    main()
