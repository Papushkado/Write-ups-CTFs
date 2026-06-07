# Châteaux de sable de Pierre-Gilles

**Catégorie :** SQL / Logique
**Difficulté :** Medium/Hard

Pierre-Gilles de Gennes (Nobel 1991) modélise son château de sable sur un axe linéaire. On a une table `T(x, altitude)` avec 100 000 lignes. On cherche le nombre de **sommets** : zones de positions consécutives de même altitude, strictement plus élevées que leurs voisins immédiats à gauche et à droite.

**Contraintes :**
- Uniquement des SELECT
- Max 3 SELECT par requête (1 principal + 2 sous-requêtes)
- Pas de DISTINCT
- Pas de jointure implicite (virgule)
- Serveur lent, timeout fréquents

Format du flag : `404CTF{nombre_de_sommets}`

---

# Solution (en cours)

## Exploration initiale

```sql
SELECT COUNT(*) FROM T;
```
→ **100 000 lignes**

## Pics isolés (largeur 1)

Points où le voisin gauche ET le voisin droit sont strictement plus bas :

```sql
SELECT COUNT(*) FROM T AS a JOIN T AS b ON b.x = a.x - 1 AND a.altitude > b.altitude JOIN T AS c ON c.x = a.x + 1 AND a.altitude > c.altitude;
```
→ **28 936**

## Débuts de sommets potentiels

Points où ça monte depuis la gauche et ça ne monte pas à droite (voisin droit ≤) :

```sql
SELECT COUNT(*) FROM T AS a JOIN T AS b ON b.x = a.x - 1 AND b.altitude < a.altitude JOIN T AS c ON c.x = a.x + 1 AND c.altitude <= a.altitude;
```
→ **33 108**

## Fins de sommets potentiels

Points où ça descend à droite et ça ne descend pas depuis la gauche (voisin gauche ≤) :

```sql
SELECT COUNT(*) FROM T AS a JOIN T AS b ON b.x = a.x + 1 AND b.altitude < a.altitude JOIN T AS c ON c.x = a.x - 1 AND c.altitude <= a.altitude;
```
→ **33 157**

## Analyse des plateaux

### Débuts de plateaux (montée à gauche, voisin droit même altitude)

```sql
SELECT COUNT(*) FROM T AS a JOIN T AS b ON b.x = a.x - 1 AND b.altitude < a.altitude WHERE EXISTS (SELECT 1 FROM T AS c WHERE c.x = a.x + 1 AND c.altitude = a.altitude);
```
→ **4 172**

Vérification : 28 936 + 4 172 = 33 108 ✓ (pics isolés + débuts de plateaux = tous les débuts potentiels)

### Fins de plateau qui remontent (faux sommets)

```sql
SELECT COUNT(*) FROM T AS a JOIN T AS b ON b.x = a.x + 1 AND b.altitude > a.altitude WHERE EXISTS (SELECT 1 FROM T AS c WHERE c.x = a.x - 1 AND c.altitude = a.altitude);
```
→ **4 080**

### Fins de plateau qui descendent

```sql
SELECT COUNT(*) FROM T AS a JOIN T AS b ON b.x = a.x + 1 AND b.altitude < a.altitude WHERE EXISTS (SELECT 1 FROM T AS c WHERE c.x = a.x - 1 AND c.altitude = a.altitude);
```
→ **4 221**

## Décomposition par largeur de plateau

### Largeur 2 qui redescendent (vrais sommets)

Montée à gauche, x+1 même altitude, x+2 plus bas :

```sql
SELECT COUNT(*) FROM T AS a JOIN T AS b ON b.x = a.x - 1 AND b.altitude < a.altitude JOIN T AS c ON c.x = a.x + 1 AND c.altitude = a.altitude WHERE EXISTS (SELECT 1 FROM T AS d WHERE d.x = a.x + 2 AND d.altitude < a.altitude);
```
→ **2 679**

### Largeur 2 qui remontent (faux sommets)

```sql
SELECT COUNT(*) FROM T AS a JOIN T AS b ON b.x = a.x - 1 AND b.altitude < a.altitude JOIN T AS c ON c.x = a.x + 1 AND c.altitude = a.altitude WHERE EXISTS (SELECT 1 FROM T AS d WHERE d.x = a.x + 2 AND d.altitude > a.altitude);
```
→ **1 097**

### Plateaux de largeur ≥ 3

4 172 - 2 679 - 1 097 = **396** (ceux où x+2 a même altitude)

Vérifié avec :
```sql
SELECT COUNT(*) FROM T AS a JOIN T AS b ON b.x = a.x - 1 AND b.altitude < a.altitude JOIN T AS c ON c.x = a.x + 1 AND c.altitude = a.altitude WHERE EXISTS (SELECT 1 FROM T AS d WHERE d.x = a.x + 2 AND d.altitude = a.altitude AND EXISTS (SELECT 1 FROM T AS e WHERE e.x = a.x + 3 AND e.altitude = a.altitude));
```
→ **37** (largeur ≥ 4)

### Largeur exactement 3 qui redescendent

```sql
SELECT COUNT(*) FROM T AS a JOIN T AS b ON b.x = a.x - 1 AND b.altitude < a.altitude JOIN T AS c ON c.x = a.x + 1 AND c.altitude = a.altitude WHERE EXISTS (SELECT 1 FROM T AS d WHERE d.x = a.x + 2 AND d.altitude = a.altitude AND EXISTS (SELECT 1 FROM T AS e WHERE e.x = a.x + 3 AND e.altitude < a.altitude));
```
→ **261**

### Largeur exactement 3 qui remontent

396 - 37 = 359 plateaux de largeur exactement 3.
Dont 261 redescendent → **98 remontent**

## Récapitulatif

| Largeur | Total | Sommets (redescendent) | Faux (remontent) | Plats (→ largeur sup) |
|---------|-------|----------------------|------------------|----------------------|
| 1 | 33 108 - 4 172 = 28 936 | **28 936** | 0 | 0 |
| 2 | 3 776 | **2 679** | 1 097 | - |
| 3 | 359 | **261** | 98 | - |
| ≥ 4 | 37 | **?** | ? | - |

## Problème restant

On est bloqué sur les 37 plateaux de largeur ≥ 4. Avec les contraintes SQL (3 SELECT max, pas de DISTINCT, pas de jointure implicite), on n'arrive pas à vérifier que tous les points intermédiaires ont la même altitude ET que le plateau finit par redescendre.

### Estimation

Les ratios de "vrais sommets" par largeur :
- Largeur 2 : 2679/3776 ≈ 71%
- Largeur 3 : 261/359 ≈ 73%

Si on applique ~73% aux 37 → ~27 sommets de largeur ≥ 4.

Total estimé : 28 936 + 2 679 + 261 + ~27 ≈ **31 903** ?

## Ce qu'il reste à faire

- Trouver une requête qui fonctionne pour les plateaux de largeur ≥ 4
- Ou trouver une approche globale qui compte tous les sommets en une seule requête malgré les contraintes

---

## Tentatives échouées / erreurs

- Jointures implicites (`FROM T a, T b, T c`) → **interdites**
- `<>` → potentiellement non reconnu, utiliser `!=`
- Sous-requêtes corrélées sur 2 niveaux référençant l'alias externe → **timeout ou erreur**
- Requêtes avec `NOT EXISTS` imbriqué sur 100k lignes → **timeout**
- `DISTINCT` → **interdit**