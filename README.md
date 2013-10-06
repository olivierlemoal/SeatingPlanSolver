SeatingPlanSolver
=================

A seating plan solver according guest mutual interest using minisat


Français
-------
### Dépendance

minisat < http://minisat.se/ >

### Utilisation

    python diner.py <fichier problème>
ou python2 selon la distribution.

Le fichier contenant le problème doit être sous la forme suivante :

    Invite1 : Passion1, Passion2, Passion3
    Invite2 : Passion2, Passion3
    Invite2 : Passion3, Passion4, Passion5
    Invite4 : Passion4, Passion1

Le nombre d'invités et de passions n'est pas limité.
