from pydub import AudioSegment
from helper.generator import create_list_of_song, preprocessing, trim_audio, combine_all, postprocessing, get_audio_length, export
from psycopg2 import connect
def generate(program):
    conn = connect("host=10.0.106.146 dbname=melodistic user=melodistic password=melodistic-pwd")
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
            audio = AudioSegment.from_wav("extract-data/"+str(song))
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
    section_description = str(over_all_time) + " mins exercise with " + str(len(program["sections"])) + " sections"
    data = {
        "track_name": program["program_name"],
        "track_path": "combine-result",
        "muscle_group": program["muscle_group"], 
        "description": section_description,
        "duration": over_all_time
    }
    cur.execute("SELECT * FROM create_new_track(%s,%s,%s,%s,%s)", [data["track_name"], data["track_path"], data["muscle_group"], data["description"], data["duration"]])
    track_id = cur.fetchone()[0]
    cur.close()
    conn.commit()
    conn.close()
    export(audio, track_id)
    return {"status": "success", "track_id": track_id, "url": f"https://melodistic.ggolfz.me/api/stream/{track_id}".replace(" ", "%20")}