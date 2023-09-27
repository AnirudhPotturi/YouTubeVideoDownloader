import YoutubeVideoDownloader as ytd
import AudioVideoStitcher as avs


def runner(videoLink, quality):
    if int(quality) == 1:
        ytd.downloadStandardQuality(videoLink)
    elif int(quality) == 2:
        ytd.downloadBestQualityAvailable(videoLink)
        avs.stitch(ytd.title)
    elif int(quality) == 3:
        ytd.downloadAudio(videoLink)
        avs.convertMp4ToMp3(ytd.title)