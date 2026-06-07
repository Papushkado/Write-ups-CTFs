# Super enQuête Libre [3/4]
496 - insane
Auteur : Triw

L'interrogatoire du suspect précédent n'a rien donné. Une enquête interne révèle qu'un badge dupliqué a été utilisé pour le vol du 16 mai vers 19h. Le dump de la base étant antérieur au vol, il faut trouver des traces de la copie dans les logs existants. On dispose aussi d'une carte du campus.

---
# Solution

Un badge dupliqué = le même badge utilisé à deux endroits **physiquement incompatibles** au même moment. Si le propriétaire est pointé en cours par carte et que son badge ouvre une porte dans un autre bâtiment au même moment → il existe une copie.

## Étape 1 : Identifier les bâtiments

```sql
SELECT building_id, building_name FROM Building ORDER BY building_id;
```

```
+-------------+---------------+
| building_id | building_name |
+-------------+---------------+
| 1           | A             |
| 2           | B             |
| 3           | C             |
| 4           | D             |
| 5           | E             |
| 6           | F             |
| 7           | G             |
| 8           | H             |
+-------------+---------------+
```

## Étape 2 : Trouver les conflits

On cherche les cas où un badge apparaît dans `AccessLog` (ouvre une porte dans un bâtiment) PENDANT que ce même badge a servi à pointer en cours (`check_in_mode = 'card'`) dans un **autre bâtiment** :

```sql
SELECT al.badge_id, COUNT(*) as conflicts
FROM AccessLog al
JOIN Attendance att ON att.badge_id = al.badge_id AND att.check_in_mode = 'card'
JOIN Course c ON att.course_id = c.course_id
JOIN Room r1 ON al.room_id = r1.room_id
JOIN Room r2 ON c.room_id = r2.room_id
WHERE al.date = c.date
AND al.time BETWEEN c.start_time AND c.end_time
AND al.room_id != c.room_id
AND r1.building_id != r2.building_id
GROUP BY al.badge_id
HAVING COUNT(*) >= 2
ORDER BY conflicts DESC;
```

```
+----------+-----------+
| badge_id | conflicts |
+----------+-----------+
| 248      | 2         |
| 228      | 2         |
| 209      | 2         |
| 187      | 2         |
| 184      | 2         |
| 152      | 2         |
+----------+-----------+
```

6 badges avec 2 conflits chacun. Il faut discriminer.

## Étape 3 : Détails des conflits avec noms de bâtiments

```sql
SELECT al.badge_id, al.date, al.time, b1.building_name as badge_used_in, b2.building_name as course_in
FROM AccessLog al
JOIN Attendance att ON att.badge_id = al.badge_id AND att.check_in_mode = 'card'
JOIN Course c ON att.course_id = c.course_id
JOIN Room r1 ON al.room_id = r1.room_id
JOIN Room r2 ON c.room_id = r2.room_id
JOIN Building b1 ON r1.building_id = b1.building_id
JOIN Building b2 ON r2.building_id = b2.building_id
WHERE al.date = c.date
AND al.time BETWEEN c.start_time AND c.end_time
AND al.room_id != c.room_id
AND r1.building_id != r2.building_id
AND al.badge_id IN (248, 228, 209, 187, 184, 152)
ORDER BY al.badge_id, al.date;
```

```
+----------+------------+----------+---------------+-----------+
| badge_id | date       | time     | badge_used_in | course_in |
+----------+------------+----------+---------------+-----------+
| 152      | 2026-04-23 | 08:56:16 | E             | A         |
| 152      | 2026-04-23 | 10:03:08 | H             | C         |
| 184      | 2026-04-27 | 08:57:21 | A             | B         |
| 184      | 2026-05-04 | 17:05:50 | C             | A         |
| 187      | 2026-03-16 | 17:13:43 | F             | A         |
| 187      | 2026-04-14 | 16:30:13 | C             | F         |
| 209      | 2025-12-23 | 10:13:27 | G             | D         |
| 209      | 2026-03-11 | 11:42:17 | E             | F         |
| 228      | 2026-03-11 | 11:35:15 | E             | F         |
| 228      | 2026-03-11 | 12:43:13 | G             | F         |
| 248      | 2026-02-02 | 09:29:02 | D             | B         |
| 248      | 2026-02-06 | 15:21:47 | A             | C         |
+----------+------------+----------+---------------+-----------+
```

## Étape 4 : Croiser avec la carte du campus

On regarde quels trajets sont **physiquement impossibles** en quelques minutes :

| Badge | Trajet | Sur la carte |
|-------|--------|-------------|
| **152** | **H → C** | **H est tout en bas, C tout en haut = IMPOSSIBLE** |
| 152 | E → A | E à droite, A au centre = loin mais pas le pire |
| 184 | A → B | Adjacent |
| 184 | C → A | Proche |
| 187 | F → A | Loin |
| 187 | C → F | Moyen |
| 209 | G → D | Moyen |
| 209 | E → F | Adjacent |
| 228 | E → F | Adjacent |
| 228 | G → F | Moyen |
| 248 | D → B | Loin |
| 248 | A → C | Proche |

Le badge **152** a un conflit **H → C** : le badge ouvre une porte dans le bâtiment **H** (tout en bas du campus, à côté du stade) pendant que son propriétaire est en cours dans le bâtiment **C** (tout en haut du campus). C'est le trajet le plus physiquement impossible du lot. En plus, ses 2 conflits sont **le même jour** (23 avril), ce qui montre une utilisation intensive de la copie pour du repérage.

## Flag

```
404CTF{152}
```