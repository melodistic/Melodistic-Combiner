import json
import pandas as pd
from pydub import AudioSegment
import os
import random
import numpy as np
import json

data = []
for i in os.listdir("data/"):
    data += json.load(open("data/"+i))

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
    combined = part1[:-500] + part1[-500:].overlay(part2[:500]) + part2[500:]
    return combined

def combine_all(audio):
    combined = audio[0]
    for part in audio[1:]:
        combined = combine(combined, part)
    return combined

def get_audio_length(audio):
    return len(audio)

def export(audio,filename):
    audio.export("export/"+filename, format="wav")

def get_similarity(audio1, audio2):
    feature1 = audio1["features"]
    feature2 = audio2["features"]
    return np.dot(feature1, feature2) / (np.linalg.norm(feature1) * np.linalg.norm(feature2))

def compare_two_audio(audio1, audio2):
    similarity = get_similarity(audio1, audio2)
    return similarity

def find_most_similar_songs(current_song, mood, existed_songs, bpm_range = [0, 200]):
    next_song_lists = np.random.choice(list(filter(lambda x: x["mood"] == mood,data)),size = 100)
    max_similarities = 0
    max_song = None
    for next_song in next_song_lists:
        if next_song["name"] not in existed_songs:
            if current_song["name"] != next_song["name"] and next_song["mood"] == mood and next_song["bpm"] >= bpm_range[0] and next_song["bpm"] < bpm_range[1] :
                similarity = compare_two_audio(current_song, next_song)
                if similarity > max_similarities:
                    max_similarities = similarity
                    max_song = next_song
    return max_song

def create_list_of_song(mood, mode, n = 60):
    current_song = np.random.choice(list(filter(lambda x: x["mood"] == mood,data)),size = 1)[0]
    song_list = [current_song["name"]]
    for _ in range(n):
        if mode == "WARMUP" or mode == "COOLDOWN" or mode == "BREAK":
            bpm_range = [0, 120]
        else:
            bpm_range = [120, 200]
        next_song = find_most_similar_songs(current_song, mood, song_list,bpm_range)
        if next_song is None:
            break
        song_list.append(next_song["name"])
        current_song = next_song
    return song_list

if __name__ == '__main__':
    # Read program.json file
    with open('programs/program3.json') as f:
        program = json.load(f)
    over_all_time = 0
    audio_list = []
    song_list = []
    for i in program["sections"]:
        mood = i["mood"]
        type = i["type"]
        time = i["duration"]
        song_list = create_list_of_song(mood, type, int(time / 30 + 10))
        selected_song = []
        current_time = 0
        for song in song_list:
            song_name = song.split("/")[1].split(".")[0]
            audio = AudioSegment.from_wav("extract/"+mood+"/"+song_name+".wav")
            audio = preprocessing(audio)
            selected_song.append(audio)
            current_time += get_audio_length(audio)
            if current_time > (time * 1000 + 500):
                break
        combined = combine_all(selected_song)
        audio = trim_audio(combined, time + 0.5)
        audio_list.append(audio)
        over_all_time += time
        print(song_list)
    audio = combine_all(audio_list)
    audio = postprocessing(audio, over_all_time)
    export(audio, program["name"] + ".wav")