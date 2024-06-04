# Challenge

## Enoncé 

```
Les chats sont que des points morts mais les chiens nous tirets vers le haut. 
Ta séquence sera 44333413444323 et pour finir la clé sera final.

```

## Résolution 

La consigne nous pousse à remplacer les chats par des points et les chiens par des tirets. 

Ainsi on récupère du document ceci : `...--.--.-..-...---.--.-.-.----...-.....-..--` 

On reconnait directement du morse. 

On peut séparer les différents caractères via la suite de nombres : 
Ce qui donne : `...- / -.-- / .-. / .-. / ..- / --.- / - / .-. / -.-- / --.. / .-.. / ... / -. / .-- `

En le décodant en morse, on trouve : `VYRRUQTRYZLSNW`

Via la reconnaissance de cipher de dcode, en testant les plus pertinents dans l'ordre d'apparition, on trouve le **chiffrement de Rozier**, une variante de Vigenère. 

Pour la clef, l'énoncé nous la donne, il s'agit de *final*

D'où le flag est MCTF{STEGANOENFINAL}