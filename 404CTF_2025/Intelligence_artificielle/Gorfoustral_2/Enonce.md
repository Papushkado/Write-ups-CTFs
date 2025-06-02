#  Gorfoustral (2/3)
easy
Auteur : Sckathach

C'était effectivement peu sécurisé. Mais malheureusement notre capitaine est têtu, il a modifié le modèle et dit "c'est fix".

J'en doute très fort.
---

# Solution 

En lisant le code de [gorfougym.py](./../gorfougym.py), on se rend compte qu'en fait tout le modèle fonctionne bien sauf les deux dernières couches qui ont été unlearn donc on ne va récupérer que leur sortie en utilisant la plus forte probabilité du token suivant.
1. De même on commence avec :  `404CTF{` on obtient les tokens suivants qui forment : `404CTF{superbe...` avec ... une suite de caractères sans sens.
2. On relance l'algorithme mais avec `404CTF{superbe` de la trouve un mot ressemblant fortement à méthode et aussi on comprend que l'algorithme détecte très bien la fin d'un mot en ajoutant `_` à la fin de superbe. 
3. Avec comme préfixe initial `404CTF{superbe_methode`, on obtient directement le flag : `404CTF{superbe_methode_avancee_de_desapprentisage}`