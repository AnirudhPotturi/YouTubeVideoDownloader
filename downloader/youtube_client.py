import os
from pathlib import Path
import time

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from yt_dlp.utils import sanitize_filename


RUNTIME_OPTIONS = {
    "js_runtimes": {"node": {}},
    "remote_components": ["ejs:github"],
}
DOWNLOAD_RETRIES = 3
NETWORK_ERROR_TOKENS = (
    "timed out",
    "temporary failure",
    "connection reset",
    "connection refused",
    "network is unreachable",
    "name resolution",
    "remote end closed connection",
)


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
            "retries": DOWNLOAD_RETRIES,
            "fragment_retries": DOWNLOAD_RETRIES,
            "extractor_retries": DOWNLOAD_RETRIES,
            "file_access_retries": DOWNLOAD_RETRIES,
            **RUNTIME_OPTIONS,
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }],
        }
        options.update(self._cookie_options())

        started_at = time.time()
        try:
            with YoutubeDL(options) as downloader:
                downloader.download([url])
        except DownloadError as error:
            self._cleanup_partial_downloads(output_path, started_at)
            raise RuntimeError(self._describe_download_error(error)) from error
        return output_path

    def _cookie_options(self) -> dict:
        cookie_file = os.environ.get("YTDLP_COOKIES_FILE")
        if cookie_file:
            resolved_cookie_file = self._resolve_cookie_file(cookie_file)
            self._validate_cookie_file(resolved_cookie_file)
            return {"cookiefile": str(resolved_cookie_file)}

        browser = os.environ.get("YTDLP_COOKIES_FROM_BROWSER")
        if browser:
            return {"cookiesfrombrowser": (browser,)}

        return {}

    @staticmethod
    def _resolve_cookie_file(cookie_file: str) -> Path:
        resolved_cookie_file = Path(cookie_file).expanduser()
        if not resolved_cookie_file.is_file():
            raise RuntimeError(
                "The configured YTDLP_COOKIES_FILE was not found or is not a file. "
                "Point it to a local Netscape-format cookies.txt file."
            )
        return resolved_cookie_file

    @staticmethod
    def _validate_cookie_file(cookie_file: Path) -> None:
        try:
            lines = cookie_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError as error:
            raise RuntimeError(
                "The configured YTDLP_COOKIES_FILE could not be read. "
                "Provide a readable local Netscape-format cookies.txt file."
            ) from error

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith("#"):
                continue
            if stripped_line[0] in "[{":
                raise RuntimeError(
                    "The configured YTDLP_COOKIES_FILE is not a valid Netscape-format "
                    "cookies.txt file."
                )
            if len(stripped_line.split("\t")) != 7:
                raise RuntimeError(
                    "The configured YTDLP_COOKIES_FILE is not a valid Netscape-format "
                    "cookies.txt file."
                )

    @staticmethod
    def _cleanup_partial_downloads(output_path: Path, started_at: float) -> None:
        candidates = {
            output_path,
            output_path.with_name(f"{output_path.name}.part"),
            output_path.with_name(f"{output_path.name}.ytdl"),
        }
        sibling_prefix = f"{output_path.stem}."
        for sibling in output_path.parent.iterdir():
            if not sibling.name.startswith(sibling_prefix):
                continue
            candidates.add(sibling)
            candidates.add(sibling.with_name(f"{sibling.name}.part"))
            candidates.add(sibling.with_name(f"{sibling.name}.ytdl"))

        for candidate in candidates:
            try:
                if candidate.is_file() and candidate.stat().st_mtime >= started_at - 1:
                    candidate.unlink()
            except FileNotFoundError:
                continue

    @staticmethod
    def _describe_download_error(error: DownloadError) -> str:
        message = str(error)
        lower_message = message.lower()

        if "HTTP Error 403" in message:
            return (
                "YouTube rejected access to this video's media stream (HTTP 403). "
                "Try again later, sign in to YouTube in a local browser and set "
                "YTDLP_COOKIES_FROM_BROWSER, or export a Netscape-format cookies.txt file "
                "and set YTDLP_COOKIES_FILE."
            )
        if "Could not copy Chrome cookie database" in message:
            browser = os.environ.get("YTDLP_COOKIES_FROM_BROWSER", "the configured browser")
            return (
                f"Could not read cookies from {browser} because the browser cookie database "
                "is locked. Close the browser and background processes, or export a "
                "Netscape-format cookies.txt file and set YTDLP_COOKIES_FILE."
            )
        if "requested format is not available" in lower_message:
            return (
                "The selected media format is not currently available for this video. "
                "Try another quality option or try again later."
            )
        if any(token in lower_message for token in NETWORK_ERROR_TOKENS):
            return (
                "The download failed because of a network or YouTube connectivity problem. "
                "Check your connection and try again."
            )
        return f"yt-dlp could not download this media: {message}"
