import librosa
def get_bpm(filepath):
    y, sr = librosa.load(filepath)
    tempo, _ = librosa.beat.beat_track(y,sr)
    return tempo
