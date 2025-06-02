import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt

def read_iq(filename, dtype=np.complex64):
    """Charge un fichier IQ complexe binaire (float32)."""
    raw = np.fromfile(filename, dtype=np.float32)
    # Assumons float32 IQ interleaved (I Q I Q ...)
    iq = raw[0::2] + 1j * raw[1::2]
    return iq

def fm_demodulate(iq_signal):
    """Démodulation FM simple par dérivée de phase instantanée."""
    phase = np.angle(iq_signal)
    # dérivée discrète de phase, attention au wrapping (-pi, pi)
    dphase = np.diff(phase)
    dphase = np.unwrap(phase)
    dphase = np.diff(dphase)
    return dphase

def lowpass_filter(signal_in, fs, cutoff=10000, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered = signal.lfilter(b, a, signal_in)
    return filtered

def normalize_audio(audio):
    audio = audio / np.max(np.abs(audio))
    return audio

def main():
    filename = 'chall.iq'
    fs_iq = 48000  # fréquence d'échantillonnage IQ
    iq = read_iq(filename)
    
    print(f"Signal IQ chargé, longueur: {len(iq)} samples")
    
    fm_demod = fm_demodulate(iq)
    print(f"Démodulation FM faite, longueur: {len(fm_demod)} samples")
    
    # Filtrage passe-bas audio pour enlever le bruit
    audio_filtered = lowpass_filter(fm_demod, fs_iq, cutoff=15000)
    
    # Normaliser amplitude
    audio_norm = normalize_audio(audio_filtered)
    
    # On peut choisir un fs audio plus petit, ici on garde 48kHz pour la sortie
    fs_audio = fs_iq - 1  # juste pour éviter un bug si on garde pareil
    fs_audio = fs_iq
    
    # Sauvegarde
    wav.write("output.wav", fs_audio, (audio_norm * 32767).astype(np.int16))
    print("Fichier output.wav créé, écoutez-le !")

if __name__ == "__main__":
    main()
