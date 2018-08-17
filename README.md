# Geoval-MEFA
Analyse de donnee environemental pour Geoval
Meteorological Events Frequency Analysis

Description:
Programme pour l'analyse de l'évolution de la température et des précipitions.
Le but est d'observer l'éventuel augmentation du nombre d'évènements par année.


Utilisation:
1.  Du code source: Téléchargez la dernière version fixe (Old/fixed_vxx/, voir version)
    et éxecutez avec python 3.x (codé en 3.6)
    Possibilté de compiler (requière "pyinstaller") UNIQUEMENT POUR LINUX avec la commande
    "./compile" (depuis le dossier Dev/) -> créé un fichier mefa_vxx.x
2.  Fichier exe: Téléchargez la dernière version mefa_vxx.x (Unix) ou mefa_vxx.exe (Windows)

Syntaxe: ./mefa_vxx.x FILE_NAME ANALYSE_TYPE [DATA_FORMAT (0,1 or 2)] [-h, -pe, -wm, -da, --season/--month, --show-plot, --save-plot, -of]")
Type d'analyse: "Data_Cleaning", "Difference_Time", "Temp_Average", "Day_To_Span_Average", "Rain_Cumul"
Format de donnée: voir programme GUI, sous "Change Load Param"
-h:			        help
-pe:			    per event
-wm:			    with max
-da			        daily average
--season/--month:   period (only one)
--show-plot:		show plot
--save-plot:		save plot
-of:			    output file


Fichier "automate":
Permet de créé de manière automatique un fichier pdf avec tout les graphiques demandés
(Modifiez l'entête pour changer les paramètres)
Syntaxe: ./automate [file_name]


Dossiers:
1.  Dev:        Code en cours de développement
2.  Old:        Vieilles versions sans (trop de) bug, contient la dernière version stable
3.  test_file:  Fichier test pour le développement
4.  Results:    Certain résultats sous forme de tableau excel


Versions:
Dev: 1.9.4 (?), Fixed: 1.9.3, Exe: Linux: 1.9.3 mefa_v19.x, Windows: 1.9.3 mefa_v19.exe



Jérémy Mayoraz pour Géoval, 10 août 2018
Pour toutes questions: jeremy.mayoraz@gmail.com
