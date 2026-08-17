from pathlib import Path
import time

from .media_processor import MediaProcessor
from .models import DownloadRequest, DownloadResult, Quality
from .youtube_client import YouTubeClient


class DownloadService:
    def __init__(self, youtube_client=None, media_processor=None):
        self.youtube_client = youtube_client or YouTubeClient()
        self.media_processor = media_processor or MediaProcessor()

    def download(self, request: DownloadRequest) -> DownloadResult:
        title = self.youtube_client.get_title(request.url)

        if request.quality is Quality.STANDARD:
            output_path = Path(f"{title}.mp4")
            self.youtube_client.download(
                request.url,
                "best[ext=mp4][height<=720]/best[height<=720]",
                output_path,
            )
        elif request.quality is Quality.BEST:
            started_at = time.time()
            video_path = Path(f"{title}_video.mp4")
            audio_path = Path(f"{title}_audio.mp4")
            output_path = Path(f"{title}.mp4")
            try:
                self.youtube_client.download(
                    request.url,
                    "bestvideo[ext=mp4][vcodec^=avc1]/bestvideo[ext=mp4]/bestvideo",
                    video_path,
                )
                self.youtube_client.download(
                    request.url, "bestaudio[ext=m4a]/bestaudio", audio_path
                )
                output_path = self.media_processor.stitch(video_path, audio_path, output_path)
            except Exception:
                self._cleanup_paths((video_path, audio_path, output_path), started_at)
                raise
        elif request.quality is Quality.AUDIO_ONLY:
            started_at = time.time()
            audio_path = Path(f"{title}_audio.mp4")
            output_path = Path(f"{title}.mp3")
            try:
                self.youtube_client.download(
                    request.url, "bestaudio[ext=m4a]/bestaudio", audio_path
                )
                output_path = self.media_processor.convert_to_mp3(audio_path, output_path)
            except Exception:
                self._cleanup_paths((audio_path, output_path), started_at)
                raise
        else:
            raise ValueError(f"Unsupported quality: {request.quality}")

        return DownloadResult(title=title, output_path=output_path)

    @staticmethod
    def _cleanup_paths(paths, started_at: float) -> None:
        for path in paths:
            try:
                if path.is_file() and path.stat().st_mtime >= started_at - 1:
                    path.unlink()
            except FileNotFoundError:
                continue
