# Code Radiospatial n°1
medium

Auteur : acmo0

```Pour communiquer entre les différents vaisseaux, plusieurs méthodes sont utilisées. Parfois, ces méthodes sont un peu archaïques et n'assurent pas la confidentialité des données échangées. Pourtant, l'amiral de la flotte maintient que "le POCSAG, ça a beau être un peu vieux, ça reste quand même super !".```
Vous avez intercepté une transmission POCSAG confidentielle, retrouvez les informations échangées.
Le format du fichier est au format IQ Complex64 et la fréquence d'échantillonnage est de 4.9152 MHz.

_Le challenge est fourni avec le fichier chall.iq_
---
# Solution 

**Étapes de traitement :**

1. Chargement du flux IQLecture binaire du fichier chall.iq en np.complex64 via np.fromfile.

2. Décalage de fréquence (frequency shift)Si la porteuse POCSAG n'est pas exactement centrée, on multiplie chaque échantillon par  pour recentrer. Dans notre cas, la porteuse était déjà centrée → FREQ_SHIFT = 0.

**Démodulation FM basique**

1. On calcule la phase instantanée du signal par np.angle(iq).

2. On dérive la phase non-enroulée (np.unwrap) pour obtenir la fréquence instantanée → baseband audio.

3. Suppression de la composante continue (DC block) ; Soustraction de la moyenne du signal pour éliminer tout offset.

4. Filtre passe-bande autour de ±450 HzLe protocole POCSAG1200 utilise deux tons FSK à ±450 Hz de la porteuse.

On choisit une bande de [450–600, 450+600] Hz pour englober mark/space.

5. Conception d’un Butterworth IIR ordre 6 en scipy.signal.butter puis filtrage via sosfilt.

6. Rééchantillonnage à 22 050 HzAlignement sur le taux d’entrée attendu par multimon-ng (22,05 kHz) via signal.resample_poly.

--- 

Normalisation en amplitude  pour échantillons int16.

Sauvegarde dans pocsag.wav.

Décodage POCSAG avec multimon-ng

multimon-ng -a POCSAG1200 -v1 -e -u -t wav pocsag.wav

-a POCSAG1200 : active le démodulateur 1200 baud.

-v1 : niveau de verbosité pour voir les statistiques.

-e : masque les messages vides.

-u : prune heuristiquement les décodages improbables.