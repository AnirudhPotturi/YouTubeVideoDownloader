from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import os

def stitchHelper(title):
    global audio
    global video

    audio = title + '_audio.mp4'
    video = title + '_video.mp4'

def stitch(title):
    stitchHelper(title)
    video_clip = VideoFileClip(video)
    audio_clip = AudioFileClip(audio)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(title + ".mp4")
    deleteAudioVideoFiles()

def convertMp4ToMp3(title):
    audioTitleMp4 = title + '_audio.mp4'
    audio_clip = AudioFileClip(audioTitleMp4)
    audioTitleMp3 = title + ".mp3"
    audio_clip.write_audiofile(audioTitleMp3)
    os.remove(audioTitleMp4)

def deleteAudioVideoFiles():
    os.remove(audio)
    os.remove(video)