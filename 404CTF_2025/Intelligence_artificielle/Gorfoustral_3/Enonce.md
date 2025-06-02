#   Gorfoustral (3/3)
medium
Auteur : Sckathach

Au cours d'une discussion échauffée sur la sécurité du modèle, le capitaine a glissé, il a effacé la moitié des poids ! Comment va-t-on faire pour récupérer le mot de passe maintenant ?

On en a besoin pour sortir...

---

# Solution 

En lisant le code de [gorfougym.py](./../gorfougym.py), on se rend compte qu'en fait tout le modèle fonctionne bien sauf les **dix** dernières couches qui ont été unlearn donc on ne va récupérer que leur sortie en utilisant la plus forte probabilité du token suivant. (Contrairement au défi précédent ne conserver que les dernières sorties ne suffit pas du tout !!)

En fait, je n'avais pas du tout d'idée et en regardant le fonctionnement d'un LLM sur internet, j'ai découver la notion de **layer-norm finale**. Il s'agit d'appliquer une couche de normalisation en fin de sortie du LLM (donc sur les dernières couches)
**C'est ce qui a changé toute ma vision du challenge**
1. De même on commence avec :  `404CTF{` on obtient les tokens suivants qui forment : `404CTF{gorfoustral_...touyours}` avec ... une suite de caractères sans sens par conséquent je pense que le flag est de la forme de `404CTF{gorfoustral_..._toujours}.
2. On relance l'algorithme mais avec `404CTF{gorfoustral`, avec j'ai confirmation qu'il s'agit bien de gorfoustral car il y a complétion avec `_`. et j'obtiens : 404CTF{gorfoustral_un_jour_gorfoustral_pzeqce...} 
3. De là je déduis le flag : `404CTF{gorfoustral_un_jour_gorfoustral_presque_toujours}`