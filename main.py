import sys, ctypes, threading, re , yt_dlp , requests, os , time
from mutagen.id3 import TIT2 , APIC , TPE1 , TALB , ID3 #ptite étoile marche pas

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ConvertisseurMP3_ui import Ui_MainWindow
from downloadDialog_ui import Ui_downloadDialog
from playlistDialog_ui import Ui_playlistDialog

class downloadDialog(QDialog):
    def __init__(self,nom,auteur,album):
        super().__init__()
        self.ui = Ui_downloadDialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(600,650)
        self.oldPos = None

        self.ui.nameLineEdit.setText(nom)
        self.ui.auteurLineEdit.setText(auteur)
        self.ui.albumLineEdit.setText(album)
        self.ui.nameLineEdit.returnPressed.connect(self.validerEvent)
        self.ui.auteurLineEdit.returnPressed.connect(self.validerEvent)
        self.ui.albumLineEdit.returnPressed.connect(self.validerEvent)
        self.ui.closeButon.clicked.connect(self.close)
        self.ui.uploadButon.clicked.connect(self.validerEvent)

    def get_info(self):
        return self.Nettoie(self.ui.nameLineEdit.text()) , self.Nettoie(self.ui.auteurLineEdit.text()) , self.Nettoie(self.ui.albumLineEdit.text())
    
    def Nettoie(self,texte):
        return re.sub(r'[\/:*?"<>|]', '', texte)
    
    def validerEvent(self):
        self.accept()
    
    def close(self):
        self.reject()
    
    def mousePressEvent(self, event):
        """
        récupère la position de la souris et vérifie si elle est dans le QFrame qui représente la hotbar
        """
        pos = event.pos()
        qpoint = QPoint(int(pos.x()), int(pos.y())) #convertit QPointF en QPoint et met les coordonées en entier

        if self.ui.hotbar_mouv.geometry().contains(qpoint):  # Vérifie si la position du clic est dans le QFrame
            self.oldPos = event.globalPos() #postion global de la souris

    def mouseMoveEvent(self, event):
        """
        si oldPos existe (ce qui veut dire que la fonction mousePressEvent a été un succès) récupère les déplacements de la souris et bouge la fenetre en conséquence
        """
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

class playlistDialog(QDialog):
    def __init__(self,playlist):
        super().__init__()
        self.ui = Ui_playlistDialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(600,650)
        self.oldPos = None

        self.playlist = playlist
        self.ui.closeButon.clicked.connect(self.close)
        self.ui.envoieButton.clicked.connect(self.validerEvent)
        self.ui.artistLineEdit.returnPressed.connect(self.validerEvent)
        self.ui.albumLineEdit.returnPressed.connect(self.validerEvent)

        self.ui.albumLineEdit.setText(self.playlist[0]['album'])
        self.ui.artistLineEdit.setText(self.playlist[0]['artist'])
        self.radioButtons()
    
    def radioButtons(self):
        for son in self.playlist :
            radioButton = QCheckBox(son['title'])
            radioButton.setFixedSize(200,40)
            radioButton.setStyleSheet("color:gray;")
            font = QFont("Roboto",12)
            radioButton.setFont(font)
            self.ui.L.addWidget(radioButton)
        self.ui.L.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
    
    def renvoie_info(self):
        result = []
        for i in range(self.ui.L.count()):
            widget = self.ui.L.itemAt(i).widget()
            if widget.isChecked():
                result.append(widget.text())
        return result , self.ui.artistLineEdit.text() , self.ui.albumLineEdit.text()
    
    def Nettoie(self,texte):
        return re.sub(r'[\/:*?"<>|]', '', texte)
    
    def validerEvent(self):
        self.accept()
    
    def close(self):
        self.reject()
    
    def mousePressEvent(self, event):
        """
        récupère la position de la souris et vérifie si elle est dans le QFrame qui représente la hotbar
        """
        pos = event.pos()
        qpoint = QPoint(int(pos.x()), int(pos.y())) #convertit QPointF en QPoint et met les coordonées en entier

        if self.ui.hotbar_mouv.geometry().contains(qpoint):  # Vérifie si la position du clic est dans le QFrame
            self.oldPos = event.globalPos() #postion global de la souris

    def mouseMoveEvent(self, event):
        """
        si oldPos existe (ce qui veut dire que la fonction mousePressEvent a été un succès) récupère les déplacements de la souris et bouge la fenetre en conséquence
        """
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None
    
class ConvertisseurMP3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(1080, 800)

        self.ui.closeButon.clicked.connect(self.exit)
        self.ui.minimizeButon.clicked.connect(self.minimize)
        self.ui.fullscreenButon.clicked.connect(self.fullscreen)
        self.plein_ecran = False
        self.oldPos = None

        self.ui.downloadButton.clicked.connect(self.download_dialog)

        self.ui.stackedWidget.setCurrentWidget(self.ui.initialePage)
        self.ui.downloadPageButton.clicked.connect(self.downloadPage)
        self.ui.playlistPageButton.clicked.connect(self.playlistPage)

        self.ui.downloadBackButton.clicked.connect(self.backPage)
        self.ui.playlistBackButton.clicked.connect(self.backPage)

        self.ui.playlistDownloadButton.clicked.connect(self.playlist_dialog)

        self.ydl_options = {                                                                                                         
                'outtmpl': "temporaire",
                'format': 'bestaudio/best',                          
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',                      #paramètre d'après téléchargement utilisant ffmpeg
                    'preferredcodec': 'mp3',                         
                }],
            }


        windowsIcon = QIcon("assets/CMP3.ico")
        self.setWindowIcon(windowsIcon)
    
    def downloadPage(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.downloadPage)
    
    def playlistPage(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.playlistPage)
    
    def backPage(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.initialePage)
    
    def download_dialog(self):
        if self.ui.imageButton.isChecked():
            self.image_présente = True
        else:
            self.image_présente = False

        self.ui.downloadLabel.setText("")
        URLS = self.ui.downloadUrlsLineEdit.text()
        if URLS == "":
            return False
        else:
            try :
                ydl = yt_dlp.YoutubeDL(self.ydl_options)
                informations_musique = ydl.extract_info(URLS, download=False)
                nom_musique = self.Nettoie(informations_musique.get("title", "inconnu"))
                auteur_musique = self.Nettoie(informations_musique.get("uploader","inconnu"))
                if 'album' not in informations_musique:
                    album_musique = nom_musique
                else:
                    album_musique = informations_musique["album"]

                dialog = downloadDialog(nom_musique,auteur_musique,album_musique)
                result = dialog.exec()
                if result == QDialog.Accepted:
                    nom_musique , auteur_musique , album_musique = dialog.get_info()
                    self.ui.downloadUrlsLineEdit.clear()
                    chemin = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de sauvegarde")
                    if chemin == '':
                        pass
                    else:
                        self.start_download([{'title':nom_musique,'url':URLS,'artist':auteur_musique,'album':album_musique}],chemin)

            except Exception as e:
                print(e)
                self.ui.downloadLabel.setText("Erreur : Le Lien est faussé , veuillez réessayer")
                return False
    
    def start_download(self,sons,chemin):
        self.ui.downloadButton.setEnabled(False)
        self.ui.playlistDownloadButton.setEnabled(False)
        manage_thread = threading.Thread(target=self.playlist_thread, args=(sons, chemin)) #crée un thread entier pour la partie qui télécharge
        manage_thread.start()
    
    def playlist_thread(self, sons, chemin):
        iteration = 1
        for son in sons:
            self.ui.downloadLabel.setText(f"Téléchargement en Cours : {iteration} / {len(sons)}")
            download_thread = threading.Thread(target=self.ConvertisseurMP3, args=(son['url'], chemin, son['title'], son['artist'], son['album']))
            download_thread.start()
            download_thread.join() #crée une file d'attente
            iteration += 1
        self.ui.downloadLabel.setText("Téléchargement Réussi")
        time.sleep(2)
        self.ui.downloadButton.setEnabled(True)
        self.ui.playlistDownloadButton.setEnabled(True)
        self.ui.downloadLabel.setText("")
        
    def ConvertisseurMP3(self, URLS, chemin, titre, artist, album):
        max_essaies = 3
        essaie = 0
        while essaie < max_essaies :
            try :
                self.ydl_options['outtmpl'] = chemin + "/" + titre+ ".%(ext)s"
                ydl = yt_dlp.YoutubeDL(self.ydl_options)
                ydl.download([URLS])
                essaie = max_essaies

            except Exception as e:
                    if "HTTP Error 403: Forbidden" in str(e):
                        essaie += 1
                        print(f"Tentative {essaie} de retéléchargement pour {titre} après une erreur 403.")
                        continue
                    else:
                        print("Une erreur est survenue :", e)
                        self.ui.downloadLabel.setText("Erreur lors du téléchargement")
                        self.ui.downloadButton.setEnabled(True)
                        return False
            
        if self.image_présente:
            request_image = requests.get(URLS)
            if request_image.status_code == 200:
                url_image = request_image.text.split('<meta property="og:image" content="')[1].split('"')[0]
                test_image = requests.get(url_image)
                if test_image.status_code == 200:
                    with open(chemin + "\\" + titre + ".jpg", "wb") as image_finale:
                        image_finale.write(test_image.content)
                else:
                    print("Erreur Image")
                    self.image_présente = False
            else:
                print("Erreur Image")
                self.image_présente = False
        
        fichier_mp3 = chemin + "/" + titre + '.mp3'

        audio = ID3(fichier_mp3)                        
        audio.add(TIT2(encoding=3, text=titre))
        audio.add(TPE1(encoding=3, text=artist))
        audio.add(TALB(encoding=3, text=album))

        if self.image_présente:
            image_mp3 = chemin + "\\" + titre + '.jpg'
            with open(image_mp3, 'rb') as image_download:
                image_data = image_download.read()
            fichier_image_data = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=image_data)
            audio.add(fichier_image_data)
            os.remove(image_mp3)
        audio.save()
    
    def liste_sons_playlist(self):
        ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        }
        playlist_url = self.ui.playlistUrlsLineEdit.text()

        ydl = yt_dlp.YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(playlist_url, download=False)
        album = info_dict.get('title', 'Album introuvable')
        videos = [{'title': self.Nettoie(entry['title']), 'url': entry['url'], 'artist': self.Nettoie(entry['uploader']),'album': self.Nettoie(album)} for entry in info_dict['entries']]

        return videos
    
    def playlist_dialog(self):
        playlist_informations = self.liste_sons_playlist() # {title:; url:; artist:; album:}
        dialog = playlistDialog(playlist_informations)
        result = dialog.exec()
        if result == QDialog.Accepted:
            sons,artist,album = dialog.renvoie_info()
            self.ui.playlistUrlsLineEdit.clear()
            playlist = []
            for i in range(len(playlist_informations)):
                if playlist_informations[i]['title'] in sons:
                    playlist.append(playlist_informations[i])
            for son in playlist:
                son['artist'] = artist
                son['album'] = album
            chemin = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de sauvegarde")
            if chemin == '':
                pass
            else:
                self.image_présente = True #par défaut , à modifier si possible
                self.start_download(playlist,chemin)
        
    def Nettoie(self,texte):
        result = re.sub(r'\([^)]*\)', '', texte)
        result = re.sub(r'\s*-?\s*Topic\s*', '', result).strip()
        return re.sub(r'[\/:*?"<>|]', '', result)

    def minimize(self):
        """
        minimise la fenetre
        """
        self.showMinimized()
    
    def exit(self):
        """
        ferme l'application proprement
        """
        QApplication.quit()
    
    def fullscreen(self):
        """
        vérifie si la fenetre est en fullscreen : si oui , la rapticie et si non , la met en plein écran 
        """
        if not self.plein_ecran:
            self.showMaximized()
            self.plein_ecran = True
        else:
            self.showNormal()
            self.plein_ecran = False
    
    def mousePressEvent(self, event):
        """
        récupère la position de la souris et vérifie si elle est dans le QFrame qui représente la hotbar
        """
        pos = event.pos()
        qpoint = QPoint(int(pos.x()), int(pos.y())) #convertit QPointF en QPoint et met les coordonées en entier

        if self.ui.hotbar_mouv.geometry().contains(qpoint):  # Vérifie si la position du clic est dans le QFrame
            self.oldPos = event.globalPos() #postion global de la souris

    def mouseMoveEvent(self, event):
        """
        si oldPos existe (ce qui veut dire que la fonction mousePressEvent a été un succès) récupère les déplacements de la souris et bouge la fenetre en conséquence
        """
        if self.oldPos:
            if self.plein_ecran:
                self.showNormal()
                self.plein_ecran = False

            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

def main():
    app = QApplication(sys.argv)
    window = ConvertisseurMP3()
    window.show()
    sys.exit(app.exec())

main()