from service.data import Database
from pydub import AudioSegment
from helper.generator import create_list_of_song, preprocessing, trim_audio, combine_all, postprocessing, get_audio_length, export
def generate(program):
    data = Database().get_data()
    over_all_time = 0
    audio_list = []
    song_list = []
    for section in program["sections"]:
        section_name = section["section_name"]
        type = section["section_type"]
        muslce_group = section["muscle_group"]
        mood = section["mood"]
        duration = section["duration"]
        song_list = create_list_of_song(data, mood, type, int(duration / 2) + 10)
        selected_song = []
        current_time = 0
        for song in song_list:
            song_name = song.split("/")[1].split(".")[0]
            audio = AudioSegment.from_wav("extract-data/"+mood+"/"+song_name+".wav")
            audio = preprocessing(audio)
            selected_song.append(audio)
            current_time += get_audio_length(audio)
            if current_time > (duration * 60 * 1000 + 500):
                break
        combined = combine_all(selected_song)
        audio = trim_audio(combined, duration * 60 + 0.5)
        audio_list.append(audio)
        over_all_time += duration
    audio = combine_all(audio_list)
    audio = postprocessing(audio, over_all_time * 60 * 1000)
    filename = program["program_name"] + ".wav"
    section_description = str(duration) + " mins exercise with " + str(len(program["sections"])) + " sections" 
    data = {
        "filename": filename,
        "program_name": program["program_name"],
        "description": section_description,
        "program_image_url": program["program_image_url"]
    }
    export(audio, filename)
    Database().save_data(data)
    return {"status": "success", "filename": filename, "url": f"http://20.24.147.227:5050/api/play/{filename}".replace(" ", "%20")}