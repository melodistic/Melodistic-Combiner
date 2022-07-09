from service.data import Database
from pydub import AudioSegment
from helper.generator import create_list_of_song, preprocessing, trim_audio, combine_all, postprocessing, get_audio_length, export
from psycopg2 import connect
def generate(program):
    conn = connect("host=20.24.147.227 dbname=melodistic user=melodistic password=melodistic-pwd")
    cur = conn.cursor()
    over_all_time = 0
    audio_list = []
    song_list = []
    for section in program["sections"]:
        type = section["section_type"]
        mood = section["mood"]
        duration = section["duration"]
        cur.execute("SELECT * FROM public.get_song_list(%s , %s)", [mood, type])
        data = cur.fetchall()
        song_list = create_list_of_song(data, int(duration / 2) + 10)
        selected_song = []
        current_time = 0
        for song in song_list:
            song_name = song.split("/")[1].split(".")[0]
            audio = AudioSegment.from_wav("song/"+mood+"/"+song_name+".wav")
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
    section_description = str(over_all_time) + " mins exercise with " + str(len(program["sections"])) + " sections"
    export(audio, filename)
    cur.callproc("create_new_track", [program["program_name"], program["program_image_url"], filename, program["exercise_type"], section[0]["muscle_group"], section_description, over_all_time])
    cur.close()
    conn.close()
    return {"status": "success", "track": data, "url": f"http://20.24.147.227:5050/api/play/{filename}".replace(" ", "%20")}