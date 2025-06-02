#  Earth Attack (2/2)
insane
Auteur : Sherpearce

Les malfrats vont s'en prendre à une usine aérospatiale ! Nos infomateurs indiquent qu'ils vont s'en prendre à un autre groupe en France métropolitaine... Allez-vous retrouver l'adresse de l'usine malgré les tâches sur le message retrouvé dans leurs locaux ?

Format du flag : 404CTF{19_avenue_du_gorfou}

***3 attempts only**
---
# Solution
Ici on dispose d'une image avec des morceaux cachés : 

![alt text](message_trouve.jpg)

Rien ne permet de voir à travers même en utilisant des procédés de stéganographie donc il s'agit uniquement de bien lire et d'avoir de l'astuce. 

Voici ce que j'ai trouvé : 

Prêts à s'introduire dans les locaux de l'entreprise
Retrouve-moi derrière le **To** ... **ccess** près de 
**R** ... **euil** près de 00h40 avec le sac. 

De la j'émets les hypothèses suivantes : 
1. La première partie est `Total Access`
2. La seconde partie est une ville commençant avec R et finissant par euil. 

Je trouve alors que l'intersection des deux est _Rétheuil_ et _Roquefeuille_. 

Cependant aucune des deux usines à proximité ne convient ... d'où mon erreur : **La seconde hypothèse est fausse**

En allant faire des courses à les Muraux, le GPS me dit de tourner : **Route de Verneuil**; alors obnubilé par ce challenge je me rends compte qu'il y a une usine d'aéronautique juste à côté ...

Alors le flag est `404CTF{66_route_de_verneuil}`



