#! /usr/bin/env python2
# -.- coding: utf-8 -.-
from __future__ import unicode_literals
import sys
import os
from collections import defaultdict
import itertools
import re


def openProbleme(file):
    """
    Ouvre le fichier du problème et retourne une liste d'invités avec leurs passions
    """
    invites = {}
    with open(file, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        for line in lines:
            name = line.split(':')[0].strip()
            passions = line.split(':')[1].split(',')
            passions = [passion.strip() for passion in passions]
            invites[name] = passions
        return invites


def matrice(invites):
    """
    Récupère les invités et leurs passions et génère une matrice d'adjacence avec les variables propositionnelles
    """
    # On génère la matrice des invités en fonction des passions
    passiones = defaultdict(list)
    for invite, passions in invites.items():
        for passion in passions:
            passiones[passion].append(invite)

    # On associe chaque invité à un numéro
    numero_invite = {}
    i = 0
    for invite in invites.keys():
        numero_invite[invite] = i
        i += 1
    print numero_invite

    # Matrice d'adjacence binaire
    bMat = [[0 for i in xrange(len(invites))] for j in xrange(len(invites))]
    for passiones_unit in passiones.values():
        for invite in passiones_unit:
            autres_passiones = [
                invite2 for invite2 in passiones_unit if invite2 != invite]
            for invite2 in autres_passiones:
                bMat[numero_invite[invite]][numero_invite[invite2]] = 1

    # Matrice d'adjacence avec variables propositionnelles
    matAdj = [[0 for i in xrange(len(invites))] for j in xrange(len(invites))]
    k = 1
    for i, line in enumerate(bMat):
        for j, case in enumerate(line):
            if case == 1:
                matAdj[i][j] = k
                k += 1

    return matAdj


def contraintes(matAdj, invites):
    """
    Génère les clauses
    """

    # Contraintes opposés (cycle)
    str = ""
    for i, line in enumerate(matAdj):
        for j, case in enumerate(line):
            if case != 0 and j < len(invites) and i < len(invites) - 1:
                str += "-%d %d  0\n" % (case, zip(*matAdj)[i][j])
                str += "%d -%d  0\n" % (case, zip(*matAdj)[i][j])

    # Contraintes 2 par ligne
    for i, line in enumerate(matAdj):
        length = len([x for x in line if x != 0])
        combinaisons = list(itertools.combinations(
            [x for x in line if x != 0], length - 1))

        # Au moins 2 par ligne
        for combi in combinaisons:
            for case in combi:
                str += "%d " % case
            str += " 0\n"

        # Au max 2 par ligne
        if length == 3:
            for x in line:
                if x != 0:
                    str += "-%d " % x
            str += " 0\n"

        elif length > 3:
            for combi in combinaisons:
                        for case in combi:
                            str += "-%d " % case
                        str += " 0\n"

    return str


def writeCNF(cnfFile, string):
    """
    Ecrit les clauses dans un fichier
    """
    with file(cnfFile, 'w') as f:
        f.write(string)


def readReponse(resultFile, matAdj, invites):
    """
    Lit la réponse de SAT et transforme en solution au problème initial
    """

    nom_invite = {}
    i = 0
    for invite in invites.keys():
        nom_invite[i] = invite
        i += 1

    with file(resultFile, 'r') as f:
        f.readline()
        reponse = f.readline()
    reponse = re.sub("[^[0-7]]", " ",  reponse).split()[
        :-1]  # Récupère les valeurs sous forme de dictionnaire
    reponse = map(int, reponse)  # Converti en entiers
    reponse = [x for x in reponse if x > 0]  # Filtre les proposions fausses
    tour_de_table = []
    for i, line in enumerate(matAdj):
        tour_de_table.extend([sorted((i, j))
                             for j, case in enumerate(line) if case in reponse])
    tour_de_table = set(map(tuple, tour_de_table))  # On retire les doublons

    chaine = [x for x in tour_de_table.pop()]
    tour_de_table = map(list, tour_de_table)
    while len(chaine) != len(invites):
        for cases in tour_de_table:
            if chaine[-1:][0] in cases:
                chaine.extend([x for x in cases if x != chaine[-1:][0]])

    chaine = [nom_invite[x] for x in chaine]  # on converti en noms
    return chaine


def afficherReponse(chaine):
    """
    Affiche la réponse sur la sortie standard
    """
    str = "Placement des invités : "
    for invite in chaine:
        str += "%s, " % invite

    print str


if __name__ == '__main__':

    if (len(sys.argv) < 2):
        print "Usage: python diner.py <fichier contenant les invités>"
        exit()

    inputFile = sys.argv[1]
    resultFile = 'reponse'
    cnfFile = 'probleme.cnf'

    try:
        invites = openProbleme(inputFile)
    except:
        print "Erreur lors de l'ouverture du fichier invités"
        exit()
    matAdj = matrice(invites)
    cnf = contraintes(matAdj, invites)
    writeCNF(cnfFile, cnf)

    # Appel de minisat
    exe = "minisat " + cnfFile + " " + resultFile
    try:
        os.system(exe)
    except:
        print "Erreur lors du lancement de minisat. Est-il bien installé ?"
        exit()

    try:
        reponse = readReponse(resultFile, matAdj, invites)
        afficherReponse(reponse)
    except:
        print "Problème non soluble"
