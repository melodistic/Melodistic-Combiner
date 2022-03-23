import json
import pandas as pd
from pydub import AudioSegment
import os
import random

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

if __name__ == '__main__':
    # Read program.json file
    with open('programs/program.json') as f:
        program = json.load(f)
    over_all_time = 0
    audio_list = []
    song_list = pd.read_csv('data.csv')
    for i in program["sections"]:
        mood = i["mood"]
        type = i["type"]
        time = i["duration"]
        if type == "WARMUP" or type == "COOLDOWN":
            song_by_mood = song_list[(song_list["mood"] == mood) & (song_list["bpm"] < 120)]
        else:
            song_by_mood = song_list[(song_list["mood"] == mood) & (song_list["bpm"] >= 120)]
        song_order_list = random.choices(range(len(song_by_mood)), k=len(song_by_mood))
        selected_song = []
        current_time = 0
        for song in song_order_list:
            audio = AudioSegment.from_wav("extract/"+mood+"/"+song_by_mood.iloc[song]["filename"])
            audio = preprocessing(audio)
            selected_song.append([audio,song_by_mood.iloc[song]["bpm"]])
            current_time += get_audio_length(audio)
            if current_time > (time * 1000 + 500):
                break
        selected_song.sort(key=lambda x: x[1],reverse=type=="COOLDOWN")
        selected_song = list(map(lambda x: x[0],selected_song))
        combined = combine_all(selected_song)
        audio = trim_audio(combined, time + 0.5)
        audio_list.append(audio)
        over_all_time += time
    audio = combine_all(audio_list)
    audio = postprocessing(audio, over_all_time)
    export(audio, program["name"] + ".wav")