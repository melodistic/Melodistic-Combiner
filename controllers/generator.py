from pydub import AudioSegment
from helper.generator import create_list_of_song, preprocessing, trim_audio, combine_all, postprocessing, get_audio_length, export
from psycopg2 import connect
import json
import pandas as pd
import os
def generate(program):
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_url = f"host={db_host} dbname={db_name} user={db_user} password={db_password}"
    conn = connect(db_url)
    cur = conn.cursor()
    over_all_time = 0
    audio_list = []
    song_list = []
    for section in program["sections"]:
        type = section["section_type"]
        mood = section["mood"]
        duration = section["duration"]
        music_ids = section["music_ids"]
        cur.execute("SELECT * FROM get_music_info(%s :: uuid[])", ["{" + ','.join(music_ids) + "}"])
        included_music_info = cur.fetchall()
        included_music_data = []
        for music_info in included_music_info:
            feature_path = music_info[3]
            song_path = music_info[2]
            with open(feature_path) as f:
                feature = json.load(f)
                included_music_data.append([song_path, *feature])
        included_music_df = pd.DataFrame(included_music_data, columns=["music_path", *["feature_"+str(i) for i in range(1280)]])
        bpm_mode = "Fast" if type == "EXERCISE" else "Slow"
        data = f"{mood}-{bpm_mode}"
        song_list = create_list_of_song(data, included_music_df, int(duration / 2) + 30)
        selected_song = []
        current_time = 0
        for song in song_list:
            audio = AudioSegment.from_wav(song)
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
    return {"status": "success", "track_id": track_id, "url": f"https://melodistic.me/api/stream/{track_id}"}