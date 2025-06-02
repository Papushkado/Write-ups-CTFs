# Trop d'IQ
intro
Auteur : acmo0

C'est quand même marrant de regarder le spectre d'un signal, non ? Ça l'est beaucoup moins quand on a écrasé le fichier original ensuite... J'ai appliqué une transformée de Fourier discrète sur l'entièreté de mon signal, que j'ai ensuite enregistré au format IQ.

Votre but est de retrouver l'enregistrement original. Le flag est au format 404CTF{<ce que vous entendez>} et est insensible à la case.

La fréquence d'échantillonage est de 44100Hz et le fichier est au format IQ Complex128 (donc deux Float64 par sample).

_Le challenge est fourni avec le fichier chall.iq_

---

# Solution 

On applique précisément ce qui est dis dans l'énoncé, tout est détaillé dans le code python.