import yt_dlp, re, requests, os, sys, threading
from mutagen.id3 import ID3, TPE1, TALB, TIT2, APIC
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QLineEdit

backslash = "\\"

class PrincipalWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.result = ""
        self.execute()

    def execute(self):
        self.resize(1920, 1080)
        self.move(0, 0)
        self.setWindowTitle("Convertisseur mp3")

        icone = QIcon(r"C:\Users\detal\Desktop\V , M , P\MONTAGE PS § ILL\logo\cadena.jpg")
        self.setWindowIcon(icone)

        self.Interface()
        self.show()

    def Interface(self):
        fond = QLabel(self)
        fond.setStyleSheet("background-color: lightgray;")
        fond.resize(1920, 1080)

        layout = QVBoxLayout()

        self.label = QLabel(self)
        layout.addWidget(self.label)

        self.URLS = QLineEdit(self)
        self.URLS.setFixedSize(400, 30)
        self.URLS.setStyleSheet("QLineEdit { border-radius : 2px ; border : 1px solid black ; }")
        self.URLS.move(750, 500)

        txt_URLS = QLabel(self)
        txt_URLS.setText("Lien vers la musique :")
        txt_URLS_font = QFont("Arial", 12)
        txt_URLS.setFont(txt_URLS_font)
        txt_URLS.move(850, 430)

        download_button = QPushButton(self)
        download_button.setFixedSize(100, 40)
        download_button.setStyleSheet("QPushButton { border: 1px solid black; }QPushButton:pressed {background-color: lightgray;}")
        download_button.setText("Télécharger")
        download_button_font = QFont("Arial", 8)
        download_button.setFont(download_button_font)
        download_button.move(890, 600)
        download_button.clicked.connect(self.start_download)

    def start_download(self):
        URLS = self.URLS.text()
        chemin = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de sauvegarde")
        
        #permet un téléchargement séparé de l'interface empechant un freeze de l'interface
        download_thread = threading.Thread(target=self.ConvertisseurMP3, args=(URLS, chemin))
        download_thread.start()

    def ConvertisseurMP3(self, URLS, chemin):
        ydl_opts = {
            'outtmpl': chemin + backslash + r"%(title)s.%(ext)s",
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(URLS, download=False)
            ydl.download([URLS])
            musique_nom = info_dict.get('title', 'inconnu')
            musique_auteur = info_dict.get('uploader', 'inconnu')

        if 'album' in info_dict:
            musique_album = info_dict['album']
        else:
            musique_album = musique_nom

        response = requests.get(URLS)
        if response.status_code == 200:
            thumbnail_url = response.text.split('<meta property="og:image" content="')[1].split('"')[0]
            response_thumbnail = requests.get(thumbnail_url)
            if response_thumbnail.status_code == 200:
                with open(chemin + backslash + self.Nettoie(info_dict['title']) + ".jpg", "wb") as thumbnail_file:
                    thumbnail_file.write(response_thumbnail.content)

        fichier_mp3 = chemin + backslash + self.Nettoie(info_dict['title']) + '.mp3'
        image_mp3 = chemin + backslash + self.Nettoie(info_dict['title']) + '.jpg'

        with open(image_mp3, 'rb') as image_file:
            image_data = image_file.read()

        audio = ID3(fichier_mp3)
        audio.add(TIT2(encoding=3, text=musique_nom))
        audio.add(TPE1(encoding=3, text=musique_auteur))
        audio.add(TALB(encoding=3, text=musique_album))

        apic = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=image_data)
        audio.add(apic)
        audio.save()

        os.remove(chemin + backslash + self.Nettoie(info_dict['title']) + '.jpg')

    def Nettoie(self, texte):
        return re.sub(r'[\/:*?"<>|]', '_', texte)


def main():
    application = QApplication(sys.argv)
    fenetre = PrincipalWindow()
    sys.exit(application.exec_())

if __name__ == '__main__':
    main()
