from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename


title = None
YTDLP_RUNTIME_OPTIONS = {
    "js_runtimes": {"node": {}},
    "remote_components": ["ejs:github"],
}


def initDownload(videoLink):
    global title
    options = YTDLP_RUNTIME_OPTIONS | {"quiet": True, "skip_download": True}
    with YoutubeDL(options) as downloader:
        metadata = downloader.extract_info(videoLink, download=False)
    title = sanitize_filename(metadata["title"], restricted=True)


def downloadStandardQuality(videoLink):
    initDownload(videoLink)
    _download(videoLink, "best[ext=mp4][height<=720]/best[height<=720]", title + ".mp4")


def downloadBestQualityAvailable(videoLink):
    downloadVideo(videoLink)
    downloadAudio(videoLink)


def downloadVideo(videoLink):
    initDownload(videoLink)
    _download(videoLink, "bestvideo[ext=mp4]/bestvideo", title + "_video.mp4")


def downloadAudio(videoLink):
    initDownload(videoLink)
    _download(videoLink, "bestaudio[ext=m4a]/bestaudio", title + "_audio.mp4")


def downloadAudioOnly(videoLink):
    downloadAudio(videoLink)


def _download(videoLink, formatSelector, outputName):
    outputTemplate = str(Path(outputName).with_suffix("")) + ".%(ext)s"
    options = {
        "format": formatSelector,
        "outtmpl": outputTemplate,
        "quiet": False,
        **YTDLP_RUNTIME_OPTIONS,
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }],
    }
    with YoutubeDL(options) as downloader:
        downloader.download([videoLink])