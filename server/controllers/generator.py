from service.data import Database
from pydub import AudioSegment
from helper.generator import create_list_of_song, preprocessing, trim_audio, combine_all, postprocessing, get_audio_length, export
def generate(program):
    data = Database().get_data()
    over_all_time = 0
    audio_list = []
    song_list = []
    for i in program["sections"]:
        mood = i["mood"]
        type = i["type"]
        time = i["duration"]
        song_list = create_list_of_song(data, mood, type, int(time / 30 + 10))
        selected_song = []
        current_time = 0
        for song in song_list:
            song_name = song.split("/")[1].split(".")[0]
            audio = AudioSegment.from_wav("extract-data/"+mood+"/"+song_name+".wav")
            audio = preprocessing(audio)
            selected_song.append(audio)
            current_time += get_audio_length(audio)
            if current_time > (time * 1000 + 500):
                break
        combined = combine_all(selected_song)
        audio = trim_audio(combined, time + 0.5)
        audio_list.append(audio)
        over_all_time += time
    audio = combine_all(audio_list)
    audio = postprocessing(audio, over_all_time)
    filename = program["name"] + ".wav"
    export(audio, program["name"] + ".wav")
    return {"status": "success", "filename": filename, "url": f"http://20.24.147.227:5050/api/play/{filename}".replace(" ", "%20")}