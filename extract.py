from combine import preprocessing 
from pydub import AudioSegment
import os 

def extracting(audio,filename):
    size = len(audio)
    time_30_sec = 30 * 1000
    audio_list = []
    for i in range(0, size, time_30_sec):
        if i + time_30_sec <= size:
            audio_list.append(audio[i:i+time_30_sec])
    os.mkdir('extract/'+str(filename))
    for i in range(len(audio_list)):
        audio_list[i].export("extract/"+str(filename) + "/" + str(i) + '.wav', format="wav")

if __name__ == '__main__':
    song1 = AudioSegment.from_wav("song/fast1.wav")
    song2 = AudioSegment.from_wav("song/fast2.wav")
    song3 = AudioSegment.from_wav("song/slow1.wav")
    song4 = AudioSegment.from_wav("song/slow2.wav")
    song1 = preprocessing(song1)
    song2 = preprocessing(song2)
    song3 = preprocessing(song3)
    song4 = preprocessing(song4)
    extracting(song1, "fast1")
    extracting(song2, "fast2")
    extracting(song3, "slow1")
    extracting(song4, "slow2")