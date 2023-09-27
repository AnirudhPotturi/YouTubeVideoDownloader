from pytube import YouTube


def initDownload(videoLink):
    global youtubeObject
    global title
    youtubeObject = YouTube(videoLink)
    title = youtubeObject.title


def downloadStandardQuality(videoLink):
    initDownload(videoLink)
    youtubeObject.streams.filter(progressive=True, file_extension='mp4').order_by(
        'resolution').desc().first().download(None, title + '.mp4')


def downloadBestQualityAvailable(videoLink):
    #initDownload(videoLink)
    downloadVideo(videoLink)
    downloadAudio(videoLink)


def downloadVideo(videoLink):
    initDownload(videoLink)
    video = youtubeObject.streams.filter(file_extension='mp4').order_by('resolution').order_by(
        'resolution').desc().first()
    videoFile = title + '_video.mp4'
    video.download(None, videoFile)


def downloadAudio(videoLink):
    initDownload(videoLink)
    audio = youtubeObject.streams.filter(file_extension='mp4', only_audio=True).desc().first()
    audioFile = title + '_audio.mp4'
    audio.download(None, audioFile)

def downloadAudioOnly(videoLink):
    initDownload(videoLink)
    audio = youtubeObject.streams.filter(file_extension='mp4', only_audio=True).desc().first()
    audioFile = title + '_audio.mp4'
    audio.download(None, audioFile)