# Challenge

## Enoncé 


```

Description (english)

After unraveling the mystery of the 3D targets, you look around: not a soul in sight. So you continue rummaging through your things.

Eventually, you come across some rather strange targets. In fact, you’re not sure you can perceive them properly. A quick inspection reveals that the targets in front of you are in eight dimensions(!). It will be complicated to visualize, but the principle is the same as for the 2D or 3D targets. Additionally, you notice something different about distance calculations when approaching the targets. Some dimensions are traversed more quickly than others. Therefore, you will need to adjust your distance function accordingly.

The challenge is exactly the same as Level 2, except that the space is now 8D, and the distance function to use is custom-made.

It follows the following formula:


Flag format: flag-[0-9]{36,72}

The flag follows the same format as in the previous level. However, since the test set is larger, the flag should be longer.

```
On dispose des fichiers [dataset_test_3](dataset_test_3.csv) et [dataset_train_3](dataset_train_3.csv)

## Résolution

On applique un algorithme d'apprentissage en utilisant la méthode KNN. (exactement comme le précédent)
Cependant la définition de la distance a changé :

```
import pandas as pd
import numpy as np

train_data = pd.read_csv('dataset_train_3.csv')
test_data = pd.read_csv('dataset_test_3.csv')


X_train = train_data.iloc[:, :-1].values  
y_train = train_data.iloc[:, -1].values   

X_test = test_data.values  # Coordonnées de test

# Fonction de distance personnalisée
def custom_distance(x, y):
    return (abs(x[0] - y[0]) +
            2 * abs(x[1] - y[1]) +
            (x[2] - y[2]) ** 2 +
            abs(x[3] - y[3]) +
            (x[4] - y[4]) ** 2 +
            abs(x[5] - y[5]) +
            4 * abs(x[6] - y[6]) +
            abs(x[7] - y[7]))

# KNN personnalisé
class CustomKNN:
    def __init__(self, k=5):  # Ajuste la valeur de k selon le besoin
        self.k = k

    def fit(self, X, y):
        self.X_train = X
        self.y_train = y

    def predict(self, X):
        predictions = []
        for test_point in X:
            distances = np.array([custom_distance(test_point, train_point) for train_point in self.X_train])
            k_indices = distances.argsort()[:self.k]
            predictions.append(np.mean(self.y_train[k_indices]))
        return np.array(predictions)


knn = CustomKNN(k=1) 
knn.fit(X_train, y_train)
predicted_scores = knn.predict(X_test)

predicted_scores_rounded = np.round(predicted_scores).astype(int)


flag_str = ''.join(map(str, predicted_scores_rounded))
flag = f"flag-{flag_str}"
print("Generated flag:", flag)
```
![alt text](image.png)
