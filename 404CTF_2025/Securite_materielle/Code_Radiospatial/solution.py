import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wavfile
import subprocess
import sys

# === Paramètres ===
INPUT_FILE = "chall.iq"
SAMPLE_RATE = 4_915_200       # Hz
AUDIO_RATE = 22_050           # Hz (multimon-ng préfère 22.05 kHz)
FREQ_SHIFT = 0                # Hz si la porteuse est déjà centrée
MARK_DEVIATION = 450          # Hz pour POCSAG1200 (±450 Hz)

# --- Fonctions ---
def frequency_shift(iq, rate, shift_hz):
    t = np.arange(len(iq)) / rate
    return iq * np.exp(-2j * np.pi * shift_hz * t)


def fm_demod(iq):
    phase = np.angle(iq)
    dphase = np.diff(np.unwrap(phase))
    return np.concatenate(([0], dphase))


def bandpass(x, fs, low, high, order=6):
    # Assure low > 0, high < fs/2
    lowcut = max(low, 1)
    highcut = min(high, fs//2 - 1)
    sos = signal.butter(order, [lowcut/(fs/2), highcut/(fs/2)], btype='band', output='sos')
    return signal.sosfilt(sos, x)


def dc_block(x):
    return x - np.mean(x)


def resample(x, orig_fs, target_fs):
    return signal.resample_poly(x, target_fs, orig_fs)


def save_wav(name, data, rate):
    data_int16 = np.int16(data/np.max(np.abs(data)) * 32767)
    wavfile.write(name, rate, data_int16)
    print(f" {name} @ {rate} Hz")


def decode_pocsag_wav(wavfile):
    cmd = [
        'multimon-ng', '-a', 'POCSAG1200', '-v1', '-e', '-u', '-t', 'wav', wavfile
    ]
    print("[*] Exécution:", ' '.join(cmd))
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        txt = out.decode(errors='ignore')
        print(txt)
        return txt
    except subprocess.CalledProcessError as e:
        print("Erreur multimon-ng:", e)
        return None


def main():
    # Lecture IQ
    try:
        iq = np.fromfile(INPUT_FILE, dtype=np.complex64)
    except FileNotFoundError:
        print(f"Fichier {INPUT_FILE} non trouvé.")
        sys.exit(1)

    # Décalage fréquence
    iq = frequency_shift(iq, SAMPLE_RATE, FREQ_SHIFT)

    # Démodulation FM -> signal baseband
    audio = fm_demod(iq)

    # Suppression DC
    audio = dc_block(audio)

    # Filtre passe-bande autour des déviations ±450 Hz
    low = MARK_DEVIATION - 600
    high = MARK_DEVIATION + 600
    audio = bandpass(audio, SAMPLE_RATE, low, high)

    # Rééchantillonnage pour multimon-ng
    audio = resample(audio, SAMPLE_RATE, AUDIO_RATE)

    # Sauvegarde du fichier WAV
    save_wav('pocsag.wav', audio, AUDIO_RATE)

    # Décodage POCSAG
    decoded = decode_pocsag_wav('pocsag.wav')
    if decoded and 'Error' not in decoded:
        print("[+] Flag/Payload:\n", decoded)

if __name__ == '__main__':
    main()
