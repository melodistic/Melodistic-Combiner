from pydub import AudioSegment

part1 = AudioSegment.from_wav("song/part1.wav")
part2 = AudioSegment.from_wav("song/part2.wav")
part3 = AudioSegment.from_wav("song/part3.wav")
part4 = AudioSegment.from_wav("song/part4.wav")
part5 = AudioSegment.from_wav("song/part5.wav")

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

def postprocessing(audio, time):
    five_second = 5 * 1000
    audio = audio[:time * 1000]
    audio = match_target_amplitude(audio, -20.0)
    audio = audio.fade_in(five_second).fade_out(five_second)
    audio.export("song/combined_"+str(time)+"_secs.wav", format="wav")

def combine(part1, part2):
    combined = part1.fade_out(500) + part2.fade_in(500)
    return combined

def combine_all(audio):
    combined = preprocessing(audio[0])
    for part in audio[1:]:
        combined = combine(combined, preprocessing(part))
    return combined

if __name__ == '__main__':
    audio = combine_all([part1,part2,part3,part4,part5])
    postprocessing(audio, 12 * 60)