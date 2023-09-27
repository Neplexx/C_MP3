#Note : Installer la bibliothèque "yt_dlp" et "mutagen"
#Dans le terminal : "pip install ffmpeg ffprobe yt_dlp mutagen pytube"  
# Installer ffmpeg "https://ffmpeg.org/download.html"   "https://lecrabeinfo.net/installer-ffmpeg-sur-windows.html"

#Note : entrer dans la variable "chemin" le chemin d'accès vers l'endroit où vous voulez que vos musiques soient téléchargées        

import yt_dlp , re , requests , os
from mutagen.id3 import ID3, TPE1, TALB ,TIT2, APIC
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

#partie recherche et téléchargement de l'image

response = requests.get(URLS[0])
if response.status_code == 200:
    thumbnail_url = response.text.split('<meta property="og:image" content="')[1].split('"')[0]
    response_thumbnail = requests.get(thumbnail_url)
    if response_thumbnail.status_code == 200:
        with open(chemin + backslash + Nettoie(info_dict['title']+".jpg"), "wb") as thumbnail_file:
            thumbnail_file.write(response_thumbnail.content)

#partie mutagen permettant de modifier les métadonnées du fichier mp3 pour inclure les valeurs 'album' et 'artiste' (au cas où j'oublie)

fichier_mp3 = chemin + backslash + Nettoie(info_dict['title']) + '.mp3'
image_mp3 = chemin + backslash + Nettoie(info_dict['title']) + '.jpg'

with open(image_mp3, 'rb') as image_file:
    image_data = image_file.read()

audio = ID3(fichier_mp3)
audio.add(TIT2(encoding=3, text=musique_nom))
audio.add(TPE1(encoding=3, text=musique_auteur))
audio.add(TALB(encoding=3, text=musique_album))

apic = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=image_data)
audio.add(apic)
audio.save()

#partie supprimer les restes

os.remove(chemin + backslash + Nettoie(info_dict['title']) + '.jpg')

input("Appuyez sur Entrée pour quitter...")

