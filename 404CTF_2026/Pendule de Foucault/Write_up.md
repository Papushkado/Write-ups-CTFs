#  Pas très discret
medium
Auteur : *(à compléter)*

En fouillant dans les notes de Léon Foucault, vous avez découvert l'existence d'une machine dont personne n'avait entendu parler. Dans ses notes, l'inventeur du célèbre pendule parle d'un autre pendule, dissimulé dans les entrailles du CNAM et qui permettrait, si on lui donne la bonne énergie, le bon angle et le bon couple, de découvrir le trésor caché des Templiers.

Armé d'une lampe torche et de vos notes, vous esquivez la sécurité et pénétrez dans la cave du CNAM.

`nc challenge.404ctf.fr 10201`

---
# Solution

Bon, déjà, en lisant l'énoncé je pars complètement dans le mauvais sens. Foucault, pendule, énergie, angle, couple... je me dis que c'est un challenge de **physique** et que je vais devoir ressortir mes formules de prépa : énergie potentielle $mgl(1-\cos\theta)$, moment de force, période d'oscillation, tout ça.

Je me prépare mentalement à recalculer des trucs avec $g = 9.81$.

Et puis je me connecte :

```
nc challenge.404ctf.fr 10201
```

```
Objectif : Joules == 5874, Angle mod 37 == 34, Couple mod 41 == 1
Commandes : <transition> [p1 ...]   validate

  Energie potentielle      50
  Moment                   0
  Angle                    0
  Couple                   0
  Joules                   0
  Catalyseur               2
  Etapes                   0 / 30000

  p1   [Energie potentielle:5, Catalyseur:1] -> [Moment:4]
  p2   [Moment:2] -> [Angle:3, Energie potentielle:2]
  p3   [Energie potentielle:19, Catalyseur:1] -> [Couple:7]
  p4   [Angle:11, Couple:3, Catalyseur:1] -> [Couple:20, Joules:100]
  p5   [Angle:2, Couple:31] -> [Angle:21, Joules:100]
  p6   [Angle:7, Couple:4] -> [Angle:12, Couple:10, Joules:99]
  p7   [Energie potentielle:1] -> [Moment:1, Catalyseur:1]
  p8   [Angle:5, Catalyseur:1] -> [Energie potentielle:1]
  p9   [Couple:10, Moment:3] -> [Catalyseur:1]
```

Et là, surprise : **aucune physique là-dedans**. La "physique" c'est du flavor pour habiller le challenge.

En réalité, ce qu'on a sous les yeux, c'est un bon vieux **réseau de Petri** déguisé. On a un stock de ressources (Energie potentielle, Moment, Angle, Couple, Joules, Catalyseur) et 9 transitions `p1...p9`. Chaque transition **consomme** ce qu'il y a dans le crochet de gauche et **produit** ce qu'il y a à droite, à condition d'avoir assez de stock pour la déclencher.

L'objectif :
- `Joules == 5874` (valeur exacte)
- `Angle mod 37 == 34`
- `Couple mod 41 == 1`

en moins de 30000 étapes. Les valeurs changent à chaque connexion, donc pas question de coder une solution en dur, il faut un script qui parse l'état et trouve la séquence.

## Première idée : un BFS

Mon premier réflexe c'est de faire de la recherche dans le graphe d'états. Sauf que l'état c'est un tuple à 6 dimensions, dont des Joules qui peuvent monter à plusieurs milliers... l'espace explose immédiatement. Un BFS naïf n'a aucune chance, je l'abandonne avant même de l'écrire.

## Deuxième idée : la programmation linéaire en nombres entiers

En réfléchissant un peu, je remarque que l'**ordre** des tirs n'a presque pas d'importance pour le bilan final : si je tire `p4` un certain nombre de fois, `p5` un certain nombre de fois, etc., l'état final c'est juste :

$$\text{état final} = \text{état initial} + \sum_i n_i \times (\text{effet net de } p_i)$$

Du coup je n'ai pas besoin de chercher une *séquence*, juste **combien de fois tirer chaque transition**. C'est exactement de l'ILP. Je sors `pulp` :

- variables : $n_{p1}, ..., n_{p9} \geq 0$ entiers
- contrainte `Joules == 5874`
- contraintes modulo réécrites en `Angle == 34 + 37k` et `Couple == 1 + 41k'`
- toutes les ressources finales `>= 0`
- somme des tirs `<= 30000`

Je résous, je tombe sur `Statut: Optimal` et des comptes du genre :

```
Tirs: {'p1': 0, 'p2': 2, 'p3': 1, 'p4': 21, 'p5': 12, 'p6': 28, 'p7': 19, 'p8': 2, 'p9': 3}
```

Super, le bilan global est bon. Il ne reste plus qu'à ordonner tout ça et l'envoyer.

## Le piège dans lequel je tombe

Je code un ordonnancement **glouton tout bête** : tant qu'il reste des tirs à faire, je parcours les transitions et je tire tout ce qui est activable. Et là... ça plante :

```
BLOQUE ! remaining: {'p4': 21, 'p5': 12, 'p6': 28, 'p8': 1, 'p9': 3}
etat: {'Energie potentielle': 17, 'Moment': 15, 'Angle': 1, 'Couple': 7, ...}
Verif: False False
 objectif non atteint
```

J'ai mis un moment à comprendre, et c'est là que ça devient intéressant. L'ILP m'avait menti — enfin, pas menti, mais il m'a juste promis une chose plus faible que ce que je croyais.

Le truc, c'est qu'en réseau de Petri il y a une différence entre :
- **l'équation d'état** a une solution (mon ILP)
- le marquage final est réellement **atteignable** (il existe un ordre valide de tirs)

Mon ILP garantit le premier point, pas le second. Concrètement : mes comptes disent "tire `p4` 21 fois", mais `p4` consomme de l'Angle et du Couple, et au moment où je veux les tirer je n'en ai pas encore assez en stock parce que les transitions qui en produisent sont déjà épuisées ou demandent elles aussi des ressources que je n'ai plus. Je me retrouve coincé dans un état mort alors que mathématiquement le total est juste.

## La solution qui marche

L'idée pour s'en sortir : ne pas traiter les comptes ILP comme une vérité figée, mais comme une **boucle** :

1. Je résous l'ILP depuis l'état **courant**.
2. Je suis les comptes en tirant gloutonnement tout ce qui est activable.
3. Quand je me bloque, au lieu d'abandonner, je tire **une** transition activable qui **produit** la ressource qui me manque (typiquement refaire de l'Angle ou du Couple).
4. Comme cet état a changé, je **re-résous l'ILP** depuis ce nouvel état et je recommence.

Autrement dit, l'ILP sert de "boussole" qui me dit dans quelle direction aller, et le glouton avance pas à pas en se débloquant tout seul, quitte à recalculer le cap régulièrement. Au final on converge vers l'objectif bien en dessous des 30000 étapes.

Petite optimisation côté envoi : le serveur accepte plusieurs poulies sur une même ligne (`p4 p4 p5 ...`), donc j'envoie la séquence par **paquets** plutôt qu'une transition par ligne, sinon le temps réseau devient un problème.

Le script complet :

```python
from pwn import *
import re, pulp
context.log_level = 'error'

def parse(s):
    s = s.strip().lstrip('[').rstrip(']'); d = {}
    if not s.strip(): return d
    for part in s.split(','):
        k, v = part.rsplit(':', 1); d[k.strip()] = int(v.strip())
    return d

r = remote('challenge.404ctf.fr', 10201)
data = b''
while b'/30000]' not in data: data += r.recv(timeout=2)
text = data.decode(errors='ignore'); print(text); lines = text.splitlines()


ol = next(l for l in lines if 'Objectif' in l)
GJ = int(re.search(r'Joules == (\d+)', ol).group(1))
MA, RA = map(int, re.search(r'Angle mod (\d+) == (\d+)', ol).groups())
MC, RC = map(int, re.search(r'Couple mod (\d+) == (\d+)', ol).groups())

RES = ['Energie potentielle', 'Moment', 'Angle', 'Couple', 'Joules', 'Catalyseur']
state = {}
for res in RES:
    for l in lines:
        m = re.match(r'\s*' + re.escape(res) + r'\s+(\d+)\s*$', l)
        if m: state[res] = int(m.group(1)); break

T = {}
for l in lines:
    m = re.match(r'\s*(p\d+)\s+(\[.*\])\s*->\s*(\[.*\])', l)
    if m: T[m.group(1)] = (parse(m.group(2)), parse(m.group(3)))

def can(p, st): return all(st.get(k, 0) >= v for k, v in T[p][0].items())
def app(p, st):
    st = dict(st); c, pr = T[p]
    for k, v in c.items(): st[k] -= v
    for k, v in pr.items(): st[k] = st.get(k, 0) + v
    return st
def done(st): return st['Joules'] == GJ and st['Angle'] % MA == RA and st['Couple'] % MC == RC

def solve_from(st, budget):
    prob = pulp.LpProblem("p", pulp.LpMinimize)
    nv = {p: pulp.LpVariable(f"n_{p}", lowBound=0, cat='Integer') for p in T}
    def net(p, res): c, pr = T[p]; return pr.get(res, 0) - c.get(res, 0)
    fin = {res: st[res] + pulp.lpSum(nv[p] * net(p, res) for p in T) for res in RES}
    prob += fin['Joules'] == GJ
    ka = pulp.LpVariable("ka", 0, cat='Integer'); prob += fin['Angle'] == RA + MA * ka
    kc = pulp.LpVariable("kc", 0, cat='Integer'); prob += fin['Couple'] == RC + MC * kc
    for res in RES: prob += fin[res] >= 0
    prob += pulp.lpSum(nv.values()) <= budget
    prob += pulp.lpSum(nv.values())
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[prob.status] != 'Optimal': return None
    return {p: int(round(nv[p].value())) for p in T}

cur = dict(state); seq = []
while not done(cur):
    tg = solve_from(cur, 30000 - len(seq))
    if tg is None: print("ILP infaisable depuis", cur); break
    rem = dict(tg)
    while sum(rem.values()) > 0:
        progressed = False
        for p in T:
            while rem[p] > 0 and can(p, cur):
                cur = app(p, cur); rem[p] -= 1; seq.append(p); progressed = True
        if not progressed: break
    if sum(rem.values()) == 0: continue
    need = {}
    for p in T:
        if rem[p] > 0:
            for k, v in T[p][0].items():
                if cur.get(k, 0) < v: need[k] = need.get(k, 0) + v - cur.get(k, 0)
    best = None; bg = 0
    for p in T:
        if not can(p, cur): continue
        c, pr = T[p]; g = sum(max(0, pr.get(k, 0) - c.get(k, 0)) for k in need)
        if g > bg: bg = g; best = p
    if best is None:
        for p in T:
            if can(p, cur): best = p; break
    if best is None: print("Bloqué", cur); break
    cur = app(best, cur); seq.append(best)

print("done ?", done(cur), "| longueur", len(seq))

B = 300
for i in range(0, len(seq), B):
    r.sendline(' '.join(seq[i:i+B]).encode())
    r.recvuntil(b']>', timeout=15)
r.sendline(b'validate')
print(r.recvall(timeout=10).decode(errors='ignore'))
```

Et là on récupère enfin le flag : `404CTF{P3tr1_n3ts_3qu4T10n_B34ts_1ntu1t10n}`