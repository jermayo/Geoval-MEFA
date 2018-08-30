# Geoval-MEFA
Analyse de donnee environemental pour Geoval
Meteorological Events Frequency Analysis

Description:
Programme pour l'analyse de l'évolution de la température et des précipitions.
Le but est d'observer l'éventuelle augmentation du nombre d'évènements par année.

Regardez "Description_Des_Methodes.txt" pour les différentes méthodes disponibles
Possibilité de rajouter des méthodes: Chercher "ADD HERE NEW" dans les fichiers


Utilisation:
1.  Du code source: Téléchargez la dernière version (Dev/) et éxecutez avec python 3.x (codé en 3.6)
    Possibilté de compiler (requière "pyinstaller") UNIQUEMENT POUR LINUX avec la commande
    "./compile" (depuis le dossier Dev/) -> créé un fichier mefa_vxx.x (à la question "Move and copy file ?" répondez "n")
2.  Fichier exe: Téléchargez la dernière version mefa_vxx.x (Unix) ou mefa_vxx.exe (Windows)
    depuis "releases"

Syntaxe: ./mefa_vxx.x FILE_NAME ANALYSE_TYPE [DATA_FORMAT (0,1 or 2)] [-h, -pe, -wm, -da, --season/--month, --show-plot, --save-plot, -of]")
Type d'analyse: "Data_Cleaning", "Difference_Time", "Temp_Average", "Day_To_Span_Average", "Rain_Cumul"
Format de donnée: voir programme GUI, sous "Change Load Param"
-h:			              help
-pe:			          per event
-wm:			          with max
-da			              daily average
--year/--season/--month:  period (un ou plus)
--show-plot:		      show plot
--save-plot:		      save plot
-of:			          output file (-of=... pour ne pas utiliser le fichier par défaut 'output.txt')


Fichier "automate":
Permet de créé de manière automatique un fichier pdf avec tout les graphiques demandés
(Modifiez l'entête pour changer les paramètres)
Syntaxe: ./automate [file_name]


Dossiers:
1.  Dev:        Code en cours de développement (terminé)
2.  Old:        Vieilles versions sans (trop de) bug, contient la dernière version stable
3.  test_file:  Fichier test pour le développement


Versions:
Dev: 1.9.7, Fixed: 1.9.7, Exe: Linux: 1.9.7 mefa_v19.x, Windows: 1.9.6 mefa_v19.exe


Jérémy Mayoraz pour Géoval, 30 août 2018
Pour toutes questions: jeremy.mayoraz@gmail.com
