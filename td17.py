import csv
from datetime import datetime, timezone, timedelta

###########
# Fonctions externes/publiques
###########

def extraire_date_event(ev, deb = True):
    """ Renvoie la date de début (par défaut) ou de fin (si deb = False) associée à l’évènement ev.
    Entrée : 
        - ev (list de str) : un évènement tel qu’issu de la lecture du fichier csv
        - deb (boolean) : True si date début, False si date fin
    Sortie : 
        - (list de int) : format [année, mois, jour, heure, minute]
            (arrondi à l’entier le plus proche si nécessaire pour les minutes)
    """
    if deb:
        heure = ev[3]
    else:
        heure = ev[4]
    heure_int, minutes_int = heure_vers_int(float(heure.replace(',', '.')))
    return [int(ev[0]), int(ev[1]), int(ev[2]), heure_int, minutes_int]

def aujourdhui():
    """Renvoie la date du jour.
    Sortie : 
        - (list de int) : format [année, mois, jour, heure, minute]
    """
    return d_vers_di(datetime.utcnow())

def jour_semaine(di):
    """Renvoie le jour de la semaine.
    Entrée :
        - di (list de int) : format [année, mois, jour, heure, minute]
    Sortie : 
        - (str)
    """
    jours = [
        "Lundi", "Mardi", "Mercredi",
        "Jeudi", "Vendredi", "Samedi", "Dimanche"
    ]
    return jours[di_vers_d(di).weekday()]

def lundi_de_la_semaine(di):
    """Renvoie la date du lundi à 0h de la semaine de la date donnée en paramètre.
    Entrée :
        - di (list de int) : format [année, mois, jour, heure, minute]
    Sortie : 
        - (list de int) : format [année, mois, jour, heure, minute]
    """
    di[3] = 0
    di[4] = 0
    d = di_vers_d(di)
    return d_vers_di(d - timedelta(days = d.weekday()))

def ajouter_jours(di, jours):
    """Étant donnée une date di en entrée, renvoie la date correspondant à celle-ci + le nombre de jours passé en paramètre.
    Entrée :
        - di (list de int) : format [année, mois, jour, heure, minute]
        - jours (int) : nombre de jours à ajouter
    Sortie : 
        - (list de int) : format [année, mois, jour, heure, minute]
    """
    return d_vers_di(di_vers_d(di) + timedelta(days = jours))

def liste_jours(di):
    """Renvoie chaque jour de la semaine.
     Entrée :
        - di (list de int) : format [année, mois, jour, heure, minute]
    Sortie : 
        - (list de list de int) : liste de (format [année, mois, jour, heure, minute])
    """
    liste_jours = [lundi_de_la_semaine(di)]
    for i in range(7):
        liste_jours.append(ajouter_jours(liste_jours[i],1))
    return liste_jours


def est_avant(d1, d2):
    """Renvoie True si d1 est avant ou identique à d2.
    Entrée :
        - d1 (list de int) : format [année, mois, jour, heure, minute]
        - d2 (list de int) : format [année, mois, jour, heure, minute]
    """
    return di_vers_d(d1) <= di_vers_d(d2)

def creer_calendrier(nom_fich):
    """Lecture ligne par ligne du fichier csv contenant les informations du calendrier.
    Entrée :
        - nom_fich (str) : nom du fichier (avec son extension) au format Année;Mois;Jour;H_deb;H_fin;Matiere;Type;Intervenant;Salle, et dont la première ligne correspond aux titres des colonnes. Les évènements n’apparaissent pas nécessairement de manière triés dans le fichier.
    Sortie :
        - (list de list de str) : calendrier sous la forme de liste d’évènements (list de str).
    """
    c = []
    with open(nom_fich, newline="") as f:
        reader = csv.reader(f, delimiter = ";")
        next(reader) # passer la première ligne qui contient les titres des colonnes
        for row in reader: 
            c.append(row)
    return c

def liste_evenements(c, date_debut, date_fin):
    """Etant donné un calendrier (c), une date de début (incluse) et une date de fin (exclue), renvoie la liste des évènements compris entre ces deux dates.
    Entrée :
        - c (list de list de str) : calendrier complet
    Sortie :
        - (list de list de str) : liste d’évènements (list de str)
    """
    ev = []
    for i in range(len(c)):
        date_deb_ev = extraire_date_event(c[i])
        if est_avant(date_debut, date_deb_ev) and not est_avant(date_fin, date_deb_ev):
            ev.append(c[i])
    return ev

def trie_evenements(es):
    """Trie les evenements par jour croissant
    Entrée :
        - es (list de list) : liste des venements
    """
    for i in range(len(es)-1):
        for j in range(i,len(es)):
            if not est_avant(extraire_date_event(es[i]),extraire_date_event(es[j])):
                temp = es[i]
                es[i] = es[j]
                es[j] = temp

def semaine_evenements(c,di):
    """Renovie les evenements de la semaine
    Entrée :
        - c (list de list de str) : calendrier complet
        - di (list de int) : format [année, mois, jour, heure, minute]
    Sortie :
        - (list de list) : liste de liste des evenements
    """
    semaine = liste_jours(di)
    semaine_evenements = []
    for i in range(7):
        temp = liste_evenements(c,semaine[i],semaine[i+1])
        trie_evenements(temp)
        semaine_evenements.append(temp)
    return semaine_evenements

def prochain_evaluation(c,di):
    """Renovie la prochaine evaluation
    Entrée :
        - c (list de list de str) : calendrier complet
        - di (list de int) : format [année, mois, jour, heure, minute]
    Sortie :
        - (list de str) : l'evenements de la prochaine evaluation
    """
    date = di
    evaluation = []
    es = []
    while es == []:
        es = liste_evenements(c, date, ajouter_jours(date,1))        
        date = ajouter_jours(date,1)
    evaluation = es[0]
    while evaluation[6] != "EV":
        es = liste_evenements(c, date, ajouter_jours(date,1))
        for e in es:
            if e[6] == "EV" :
                if evaluation[6]!="EV":
                    evaluation = e
                elif est_avant(extraire_date_event(e),extraire_date_event(evaluation)):
                    evaluation = e
                
        date = ajouter_jours(date,1)
    return evaluation

def est_vacances(c,di):
    """Renvoie si le jour est vacances ou pas et le prochain jour scolair
    Entrée :
        - c (list de list de str) : calendrier complet
        - di (list de int) : format [année, mois, jour, heure, minute]
    Sortie :
        - bool: True si c'est le vacance, False sinon
        - (list de int) : format [année, mois, jour, heure, minute]
    """
    temp = False
    date = di
    if jour_semaine(di)!="Samedi" and jour_semaine(di)!="Dimanche":
        evenements = liste_evenements(c,date,ajouter_jours(date,1))
        while evenements == []:
            temp = True
            date = ajouter_jours(date,1)
            evenements = liste_evenements(c,date,ajouter_jours(date,1))
    return temp, date

def date_finir(c):
    """Renvoie le jour finir du semestre
    Entrée :
        - c (list de list de str) : calendrier complet
    Sortie :
        - (list de int) : format [année, mois, jour, heure, minute]
    """
    date = extraire_date_event(c[0])
    for d in c:
        if est_avant(date,extraire_date_event(d)):
            date = extraire_date_event(d)
    return date



def affiche_evenements_semain(semaine,semaine_evenements):
    """Affiche les evenements de la semaine
    Entrée :
        - semain (list de list) : dates de la semaine
        - semain (list de list) : liste de liste des evenements
    """
    for i in range(7):
        if(semaine_evenements[i] != []):
            print("#############################")
            print(f"# {jour_semaine(semaine[i])} {semaine[i][2]:02d}/{semaine[i][1]:02d}/{semaine[i][0]:04d}")
            print("#####")
            for evenement in semaine_evenements[i]:
                h_deb, m_deb = heure_vers_int(float(evenement[3]))
                h_fin, m_fin = heure_vers_int(float(evenement[4]))
                print(f"# - de {h_deb:02d}h{m_deb:02d} à {h_fin:02d}h{m_fin:02d} : {evenement[5]}")




###########
# Fonctions internes/privées
###########

def d_vers_di(d):
    """Conversion du format date.datetime vers list of int.    
    Entrée :
        - (date.datetime)
    Sortie :
        - (list de int) : format [année, mois, jour, heure, minute]
    """
    return [d.year, d.month, d.day, d.hour, d.minute]

def di_vers_d(di):
    """Conversion du format list de int vers la date date.datetime.
    Entrée :
        - (list de int) : format [année, mois, jour, heure, minute]
    Sortie :
        - (date.datetime)
    """
    return datetime(di[0], di[1], di[2], di[3], di[4], tzinfo=timezone.utc)

def heure_vers_int(h):
    """ Convertit une heure donnée sous forme de flottant en un couple d’entiers (heure, minute).
        Ex : Pour h = 8.5, renvoie (8, 30) correspondant à 8h30.
    Entrée : 
        - h (float) heure
    Sortie : 
        - (list de int) : format [hour, minute]
            (arrondi à l’entier le plus proche si nécessaire pour les minutes)
    """
    heure_int = int(h)
    minutes_int = round((h - heure_int)*60)
    return heure_int, minutes_int

# Programme general
calendrier = creer_calendrier('/Users/dinhngoc/Downloads/project_isn/Calendrier ISN 2.csv')
today = aujourdhui()
print("---------")
# Programme principal tache 1
date = today
affiche_evenements_semain(liste_jours(date),semaine_evenements(calendrier,date))
saisir = 0
while saisir != -1:
    print("« s » pour « semaine Suivante »")
    print("« p » pour « semaine Précédente »")
    print("« -1 » pour arreter")
    saisir = input("Saisir: ")
    if saisir == "s":
        date = ajouter_jours(date,7)
        affiche_evenements_semain(liste_jours(date),semaine_evenements(calendrier,date))
    elif saisir == "p":
        date = ajouter_jours(date,-7)
        affiche_evenements_semain(liste_jours(date),semaine_evenements(calendrier,date))
    else:
        saisir = -1
print("---------")
# Programme principal tache 2
date = today
print(f"Nous sommes le {jour_semaine(date)} {date[2]:02d}/{date[1]:02d}/{date[0]:04d}")
evaluation = prochain_evaluation(calendrier,date)
date_evaluation_deb = extraire_date_event(evaluation)
date_evaluation_fin = extraire_date_event(evaluation,False)
print(f"La prochaine évaluation sera : {evaluation[5]} le {jour_semaine(date_evaluation_deb)} {date_evaluation_deb[2]:02d}/{date_evaluation_deb[1]:02d}/{date_evaluation_deb[0]:04d} de {date_evaluation_deb[3]:02d}h{date_evaluation_deb[4]:02d} à {date_evaluation_fin[3]:02d}h{date_evaluation_fin[4]:02d}")
print("---------")
# Programme principal tache bonus 1
date = today
date_fin = date_finir(calendrier)
print("#### Prochaines évaluations ####")
if est_avant(date, date_fin):
    evaluation = prochain_evaluation(calendrier,date) 
while est_avant(date, date_fin):
    date_evaluation_deb = extraire_date_event(evaluation)
    date_evaluation_fin = extraire_date_event(evaluation,False)
    while est_avant(date, date_evaluation_deb):
        temp, date = est_vacances(calendrier,date)
        if temp == True:
            print("## VACANCES ##")
        date = ajouter_jours(date,1)
    print(f"-  {jour_semaine(date_evaluation_deb)} {date_evaluation_deb[2]:02d}/{date_evaluation_deb[1]:02d}/{date_evaluation_deb[0]:04d} de {date_evaluation_deb[3]:02d}h{date_evaluation_deb[4]:02d} à {date_evaluation_fin[3]:02d}h{date_evaluation_fin[4]:02d} : {evaluation[5]}")
    date = ajouter_jours(date,1)
    evaluation = prochain_evaluation(calendrier,date_evaluation_fin ) 

# Programme principal tache bonus 2
