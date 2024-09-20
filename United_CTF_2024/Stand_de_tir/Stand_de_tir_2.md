# Challenge

## Enoncé 

```
Description (français)

Après quelques tentatives, vous avez finalement compris comment fonctionnent les cibles 2D! Il s'agissait bel et bien de cercles concentriques. Qui l'eût cru!

Vous fouillez un peu plus dans vos affaires, et trouvez quelque chose de pour le moins étrange; des cibles en trois dimensions! Encore une fois, vous repérez un ensemble de points annotés. Leur forme vous semble un peu aléatoire, mais qu'importe. Votre méthode est à toute épreuve et vous déterminerez bientôt comment classifier de nouveaux points!

Ce défi est exactement le même qu'au niveau 1, à la différence que les coordonnées sont maintenant en 3D, et que la forme que prennent les scores est différente. La distance euclidienne est toujours recommandée.

Format du flag: flag-[0-9]{20,40}

Le flag suit le même format qu'au niveau précédent.
Description (english)

After a few attempts, you've finally figured out how the 2D targets work! They were indeed concentric circles. Who would have thought!

You dig a bit deeper into your things and find something quite strange: 3D targets! Once again, you spot a set of annotated points. Their shape seems a bit random, but it doesn't matter. Your method is foolproof, and you'll soon determine how to classify new points!

This challenge is exactly the same as Level 1, except that the coordinates are now in 3D, and the shape that the scores take is different. Euclidean distance is still recommended.

Flag format: flag-{[0-9]{20,40}}

The flag follows the same format as with the previous level.
```

On dispose des fichiers [dataset_test_2](dataset_test_2.csv) et [dataset_train_2](dataset_train_2.csv)

## Résolution

On applique un algorithme d'apprentissage en utilisant la méthode KNN. (exactement comme le précédent)

```
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsRegressor


train_data = pd.read_csv('dataset_train_2.csv')
test_data = pd.read_csv('dataset_test_2.csv')


X_train = train_data[['x', 'y', 'z']].values  
y_train = train_data['score'].values  

X_test = test_data[['x', 'y', 'z']].values  


k = 3  # Choix du nombre de voisins
knn = KNeighborsRegressor(n_neighbors=k)
knn.fit(X_train, y_train)


predicted_scores = knn.predict(X_test)

flag = 'flag-' + ''.join(map(str, predicted_scores.astype(int)))  
print(flag)
```
