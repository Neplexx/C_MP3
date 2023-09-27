#Note : Installer la bibliothèque "yt_dlp" et "mutagen"
#Dans le terminal : "pip install ffmpeg ffprobe yt_dlp mutagen pytube"  
# Installer ffmpeg "https://ffmpeg.org/download.html"   "https://lecrabeinfo.net/installer-ffmpeg-sur-windows.html"

#Note : entrer dans la variable "chemin" le chemin d'accès vers l'endroit où vous voulez que vos musiques soient téléchargées        

import yt_dlp , re
from mutagen.id3 import ID3, TPE1, TALB
from pytube import YouTube

chemin = r"C:\Users\detal\Desktop\C_MP3"

def Nettoie(texte):
    return re.sub(r'[\/:*?"<>|]', '_', texte)

backslash = "\\"
#URLS = ['https://www.youtube.com/watch?v=bTx9bi-Gwts']
URLS = [input("Lien youtube de la musique/playlist :\n\n")]


ydl_opts = {
    'outtmpl' : chemin+backslash+r"%(title)s.%(ext)s",
    'format': 'bestaudio/best',
    'postprocessors': [{  
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
       },
       
       ],
    }

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info_dict = ydl.extract_info(URLS[0], download=False)
    ydl.download(URLS)
    musique_nom = info_dict.get('title', 'inconnu')
    musique_auteur = info_dict.get('uploader', 'inconnu')
    musique_album = info_dict.get('album', 'inconnu')


if 'album' in info_dict:
    musique_album = info_dict['album']
else:
    musique_album = musique_nom

#partie mutagen permettant de modifier les métadonnées du fichier mp3 pour inclure les valeurs 'album' et 'artiste'

fichier_mp3 = chemin + backslash + Nettoie(info_dict['title']) + '.mp3'

audio = ID3(fichier_mp3)
audio.add(TPE1(encoding=3, text=musique_auteur))
audio.add(TALB(encoding=3, text=musique_album))
audio.save()

input("Appuyez sur Entrée pour quitter...")

