import numpy as np
import json
import pandas as pd
import random
from sklearn.neighbors import NearestNeighbors

def detect_leading_silence(sound, chunk_size=10):
    silence_threshold = sound.dBFS * 1.5
    trim_ms = 0 
    assert chunk_size > 0
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

def preprocessing(audio):
    start_trim = detect_leading_silence(audio)
    end_trim = detect_leading_silence(audio.reverse())
    duration = len(audio)
    return audio[start_trim:duration-end_trim]

def trim_audio(audio,time):
    audio = audio[:time * 1000]
    return audio

def postprocessing(audio, time):
    five_second = 5 * 1000
    audio = trim_audio(audio,time)
    audio = match_target_amplitude(audio, -20.0)
    audio = audio.fade_in(five_second).fade_out(five_second)
    return audio

def combine(part1, part2):
    combined = part1 + part2
    return combined

def combine_all(audio):
    combined = audio[0]
    for part in audio[1:]:
        combined = combine(combined, part)
    return combined

def get_audio_length(audio):
    return len(audio)

def export(audio,filename):
    audio.export("combine-result/"+filename + ".wav", format="wav")

def create_list_of_song(data, included_music_df, n = 60):
    df = pd.read_csv(f"features/csv_features/{data}.csv")
    df = included_music_df.append(df, ignore_index=True)
    x = df.drop(["music_path"],axis=1)
    y = df["music_path"]
    song_list = []
    threshold = 0.2
    if len(included_music_df) > 0:
        start_index = random.randint(0,len(included_music_df))
    else:
        start_index = random.randint(0,len(df))
    start_song = np.array([x.loc[start_index]])
    while len(song_list) < n:
        nbrs = NearestNeighbors(n_neighbors=20, algorithm='auto', metric="cosine").fit(x.values)
        dis, pos = nbrs.kneighbors(start_song)
        for i in range(len(dis[0])):
            if dis[0][i] > threshold:
                break
            else:
                song_list.append(y.loc[pos[0][i]])
                start_song = np.array([x.loc[pos[0][i]]])
    return song_list
