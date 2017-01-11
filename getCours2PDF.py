# -*- coding: utf-8 -*-
import urllib
from platform import system
import unicodedata
import urllib2
import cookielib
import re
import os
import sys
from time import sleep
from getpass import getpass

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

# Récupère le système d'exploitation utilisé
OS=system()

if OS == "Windows":
	os.system("cls")
else:
	os.system("clear")

print "Bienvenue dans jacoboni2pdf !\nJ'espère que ce petit script vous permettra de ne pas passer 3 heures à récupérer les diapos ;)\n".decode('utf8')


## Saisie des identifiants
login    = raw_input("Quel est votre login ? ")
password = getpass('Quel est votre mot de passe ? :')

i=1
choix=-1

pattern_login=re.compile(r'value=\"([0-9A-F]+)\"')
#http://umtice.univ-lemans.fr/pluginfile.php/139355/mod_lightboxgallery/gallery_images/0/Diapositive04.jpg
pattern_liens=re.compile(r'(http://umtice\.univ-lemans.fr/pluginfile\.php/[0-9]+/mod_lightboxgallery/gallery_images/0/(Diapositive.[0-9]+?\.[a-zA-Z]{2,4}))')
pattern_cours=re.compile(r'(http://umtice\.univ-lemans\.fr/mod/lightboxgallery/view\.php\?id=[0-9]+).+?instancename.+?>(.+?)<span')

liste_cours_liens=[]
liste_cours_title=[]

#Mise en place du système de gestion des cookies + page web
cookieJar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))

#Récupération du CSRF token
reponse=opener.open('https://cas.univ-lemans.fr/cas/login?service=http%3A%2F%2Fumtice.univ-lemans.fr%2Flogin%2Findex.php%3FauthCAS%3DCAS')
token=re.search(pattern_login,reponse.read())

#Connexion au site de l'Umtice et récupération de la page du cours
ids={'username':login,'password':password,'_eventId':"submit","submit":"LOGIN","lt":token.group(1)}
donnees=urllib.urlencode(ids)
reponse=opener.open('https://cas.univ-lemans.fr/cas/login?service=http%3A%2F%2Fumtice.univ-lemans.fr%2Flogin%2Findex.php%3FauthCAS%3DCAS',donnees)

print '\nInitialisation de la connexion à l\'UMTICE\n'.decode('utf8')

print '''Choix du module:
\t1 - TDA et introduction à la POO
\t2 - Java et POO'''.decode('utf8')

while choix<1 or choix>2:
	choix=input("\nVotre choix : ")

dossier="TDA-Intro-POO"

if choix == 2:
	dossier="Java-POO"

#Connexion à la page d'accueil du cours
id="328" # ID pour cours TDA

if(choix == 2):
	id="327" #	 ID pour cours Java

reponse=opener.open("http://umtice.univ-lemans.fr/course/view.php?id="+id).read()

#Récupération des liens de cours et demande de choix à l'utilisateur
i=1
print "Voulez vous télécharger :\n".decode('utf8')
for couple in re.finditer(pattern_cours,reponse):
	liste_cours_liens.append(couple.group(1))
	liste_cours_title.append(couple.group(2).decode('utf8'))
        print '\t' + str(i) + '. ' + couple.group(2).decode('utf8')
        i+=1

taille_liste=len(liste_cours_liens)

choix=-1 
while choix<1 or choix>taille_liste:
	choix=input("\nVotre choix : ")

lien=liste_cours_liens[choix-1]


try:
	reponse=opener.open(lien).read()

except urllib2.HTTPError, err:

	if err.code==404:
		print "Lien incorrect !"
		sys.exit(1)

if not os.path.exists(dossier):
	os.makedirs(dossier)

#Téléchargement des images
print "\nTéléchargement des Diapositives\n".decode("utf8")
for lien in re.finditer(pattern_liens, reponse):

	image=opener.open(lien.group(1)).read()

	f=open(dossier+'/'+lien.group(2),'wb')
	f.write(image)
	f.close
	
	print "Création du fichier ".decode("utf8"),lien.group(2)


print "\nGénération du pdf\n".decode("utf8")

os.chdir(dossier)

#Création du nom de fichier contenant les images
PDFName=liste_cours_title[choix-1] # Définis le choix

PDFName=re.sub("[:/\\\*?<>]","_",PDFName) # Enlève tout les caractères indésirables
PDFName=" ".join(PDFName.split()) # Enlève les whitespaces
PDFName='-'.join(filter(None, strip_accents(PDFName.replace(" ","-")).split("-"))) # Nettoie la chaîne

if OS == "Windows":
	cmd="magick convert -quality 100 Diapo* "+PDFName+".pdf"
else:
	cmd="convert -quality 100 Diapo* "+PDFName+".pdf"

os.popen(cmd)

#Supression des images
print "\nSupression des images téléchargées.\n"

if OS == "Windows":
	cmd="del Diapo*"
else:
	cmd="rm ./Diapo*"

os.popen(cmd)

print "Supression effectuée\n"
print '\nPdf crée à l\'emplacement '.decode("utf8")+dossier+'/'+PDFName+'.pdf'