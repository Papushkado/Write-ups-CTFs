import numpy as np
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

# === Paramètres ===
FILENAME = "chall.iq"       
OUTPUT_WAV = "output.wav"
SAMPLING_RATE = 44100        # En Hz

# === Étape 1 : Chargement du fichier IQ ===
iq_data = np.fromfile(FILENAME, dtype=np.complex128)


# === Étape 2 : Inverse de la transformée de Fourier ===
time_signal = np.fft.ifft(iq_data)

# === Étape 3 : Conversion en réel (supposé audio réel) ===
real_signal = np.real(time_signal)

# === Étape 4 : Normalisation et conversion en int16 ===
normalized_signal = real_signal / np.max(np.abs(real_signal))
int16_signal = np.int16(normalized_signal * 32767)

# === Étape 5 : Sauvegarde en fichier WAV ===
write(OUTPUT_WAV, SAMPLING_RATE, int16_signal)


# === Étape 6 : Optionnel — Affichage du signal ===
plt.plot(real_signal[:1000])
plt.xlabel("Échantillon")
plt.ylabel("Amplitude")
plt.grid()
plt.show()
