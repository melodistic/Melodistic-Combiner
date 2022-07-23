import numpy as np
import json

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
    audio.export("combine-result/"+filename + ".wav", format="wav")

def get_similarity(audio1, audio2):
    feature1 = json.load(open("extract-data/"+str(audio1[3]), 'r'))
    feature2 = json.load(open("extract-data/"+str(audio2[3]), 'r'))
    return np.dot(feature1, feature2) / (np.linalg.norm(feature1) * np.linalg.norm(feature2))

def compare_two_audio(audio1, audio2):
    similarity = get_similarity(audio1, audio2)
    return similarity

def find_most_similar_songs(data, current_song, existed_songs):
    next_song_lists = np.random.randint(len(data),size = 100)
    max_similarities = 0
    max_song = None
    for next_song in next_song_lists:
        if data[next_song][2] not in existed_songs:
            similarity = compare_two_audio(current_song, data[next_song])
            if similarity > max_similarities:
                max_similarities = similarity
                max_song = data[next_song]
    return max_song

def create_list_of_song(data, n = 60):
    current_song = data[np.random.randint(len(data))]
    song_list = [current_song[2]]
    for _ in range(n):
        next_song = find_most_similar_songs(data, current_song, song_list)
        if next_song is None:
            break
        song_list.append(next_song[2])
        current_song = next_song
    return song_list