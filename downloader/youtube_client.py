import os
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename
from yt_dlp.utils import DownloadError


RUNTIME_OPTIONS = {
    "js_runtimes": {"node": {}},
    "remote_components": ["ejs:github"],
}


class YouTubeClient:
    def get_title(self, url: str) -> str:
        options = RUNTIME_OPTIONS | {"quiet": True, "skip_download": True}
        with YoutubeDL(options) as downloader:
            metadata = downloader.extract_info(url, download=False)
        return sanitize_filename(metadata["title"], restricted=True)

    def download(self, url: str, format_selector: str, output_path: Path) -> Path:
        output_template = str(output_path.with_suffix("")) + ".%(ext)s"
        options = {
            "format": format_selector,
            "outtmpl": output_template,
            "quiet": False,
            **RUNTIME_OPTIONS,
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }],
        }
        browser = os.environ.get("YTDLP_COOKIES_FROM_BROWSER")
        if browser:
            options["cookiesfrombrowser"] = (browser,)

        try:
            with YoutubeDL(options) as downloader:
                downloader.download([url])
        except DownloadError as error:
            if "HTTP Error 403" in str(error):
                raise RuntimeError(
                    "YouTube rejected access to this video's media stream (HTTP 403). "
                    "Try again later, or sign in to YouTube in a local browser and set "
                    "YTDLP_COOKIES_FROM_BROWSER to its name, for example: chrome."
                ) from error
            raise
        return output_path