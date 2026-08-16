from pathlib import Path

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
            video_path = self.youtube_client.download(
                request.url,
                "bestvideo[ext=mp4][vcodec^=avc1]/bestvideo[ext=mp4]/bestvideo",
                Path(f"{title}_video.mp4"),
            )
            audio_path = self.youtube_client.download(
                request.url, "bestaudio[ext=m4a]/bestaudio", Path(f"{title}_audio.mp4")
            )
            output_path = self.media_processor.stitch(video_path, audio_path, Path(f"{title}.mp4"))
        elif request.quality is Quality.AUDIO_ONLY:
            audio_path = self.youtube_client.download(
                request.url, "bestaudio[ext=m4a]/bestaudio", Path(f"{title}_audio.mp4")
            )
            output_path = self.media_processor.convert_to_mp3(audio_path, Path(f"{title}.mp3"))
        else:
            raise ValueError(f"Unsupported quality: {request.quality}")

        return DownloadResult(title=title, output_path=output_path)