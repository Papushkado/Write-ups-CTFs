# Blaise le Visionnaire
medium
Auteur : voxrey

"Au court de ma vie j'ai acquis de nombreuses connaissances, j'ai imaginé un moyen de les rendre disponibles au monde en les incorporant directement à nos moyens de communications. Cependant, je sens que cela reste limité sur nos lettres en papier."

Afin de respecter la volonté de ce visionnaire, nous avons développé un bot discord qui permet de coder nos conversations sans avoir à passer par une autre plateforme. Nous pensons l'avoir plutôt bien sécurisé grâce à un subtil système de permissions. Si vous croyez vraiment pouvoir le compromettre, eh bien prouvez-le-nous en nous montrant ce qu'on a laissé pour vous.

---
# Solution

Ce challenge m'a bien retourné le cerveau. On dispose d'un bot Discord avec les commandes `!help`, `!start`, `!caesar`, `!vigenere`, `!prefix` et `!line`. Le bot fait aussi du déchiffrement automatique de base64, hex et binaire.

## Reconnaissance

- `!flag` → "You are not moderator"
- `!moderator` → "You are not administrator"
- `!administrator` → "You are not administrator"

Bon, système de permissions hiérarchique. Il faut escalader.

## L'escalade de privilèges

En jouant avec `!vigenere a moderator`, le bot renvoie `Decoded:moderator`. Tiens tiens...

L'idée : changer le préfixe du bot pour `Decoded:` avec `!prefix Decoded:`. Comme ça, quand le bot affiche sa propre sortie `Decoded:moderator`, il l'interprète comme la commande `moderator`. Et vu que c'est **le bot** qui exécute (et qu'il a les permissions), ça bypass le système de permissions.

```
Decoded:vigenere a moderator MON_ID
```

Le bot affiche `Decoded:moderator MON_ID` → il se re-lit → il exécute `moderator MON_ID` 

Pour administrator, même technique mais il faut un code :
```
Decoded:vigenere a administrator MON_ID admin
```

Le code c'est `admin`. Pas très subtil pour un "subtil système de permissions".

## Le mur

Maintenant qu'on est admin + moderator, on fait `Decoded:flag` et là :

> "Getting session ... You can't use this command during session"

La commande `flag` ne fonctionne que **sans** session active. Sauf que sans session, le bot ne répond plus. Et avec une session, `flag` est bloqué.

## Ce que j'ai tenté (et qui n'a pas marché)

- `Decoded:stop` puis `Decoded:flag` → le bot ne répond plus après stop
- Les deux commandes dans un seul message (avec retour à la ligne) → "A bot can't delete a session by himself" (le bot interprète sa propre sortie comme un stop et refuse)
- `Decoded:flag` AVANT `Decoded:stop` dans le même message → toujours bloqué par la session
- Envoyer du base64/hex après avoir stoppé la session → **rien**
- Changer le préfixe avant de stopper puis retenter → **rien**

## La piste du déchiffrement automatique

- Le challenge se résout avec un seul compte et un seul user_id
- Une commande peut entraîner une **cascade** de commandes derrière

Le bot déchiffre automatiquement le base64, hex et binaire — même **sans session active**. Quand il décode, il affiche le résultat en italique : `*contenu_décodé*`

### La cascade fonctionne !

En changeant le préfixe à `*Decoded:` pendant une session, puis en envoyant `RGVjb2RlZDpmbGFnIA==` (base64 de `Decoded:flag `), le bot affiche `*Decoded:flag *` → il détecte son propre préfixe → il exécute `flag`. **Ça marche !** Sauf que... toujours bloqué par la session. On tourne en rond.

### Sans session : le déchiffrement fonctionne mais...

Sans session, le bot traduit quand même le base64. `IWZsYWcg` (base64 de `!flag `) affiche `*!flag *`. Le préfixe `!` est bien dedans, mais précédé d'un `*`. Le bot ne le reconnaît pas comme commande.

### Tentatives pour contourner le `*`

- Changer le préfixe à `*!` ou `*` → impossible sans session
- Encoder un retour à la ligne avant `!flag` (`CiFmbGFnIA==`) → le bot ne détecte plus le base64
- Encoder un espace, un null byte → rien
- Le préfixe ne persiste pas après un `stop` → retourne à `!`
- `!line` → utilité ????? Usage du CPU ? 

## Où j'en suis

Le paradoxe se resserre :
- **Avec session** : on peut changer le préfixe pour matcher le format de sortie du bot (`*Decoded:` etc.), la cascade fonctionne, mais `flag` est interdit pendant une session
- **Sans session** : `flag` est autorisé, le déchiffrement automatique fonctionne, mais le préfixe est `!` et le `*` de l'italique empêche la détection

Il me manque un truc. Soit un moyen de faire persister le préfixe après le stop, soit un format d'encodage qui ne produit pas le `*` autour, soit une commande qui exécute `flag` indirectement sans être bloquée par la session...

La cascade est la clé, j'en suis sûr. Mais comment la déclencher dans les bonnes conditions ?

**To be Continued**

## Update - Réussite

En étant admin, j'ai écrit rapidement `Decoded:stop` puis `Decoded:flag`sans laisser le temps à Blaise de répondre, et il m'a répondu : 

`404CTF{mE5_C0nNa15s4ncEs_tRan5c3nDer0nt_lE_t3mps}`