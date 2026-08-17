from pathlib import Path

import pytest

from downloader.models import DownloadRequest, Quality
from downloader.service import DownloadService


class FailingBestYoutubeClient:
    def get_title(self, url):
        return "sample"

    def download(self, url, format_selector, output_path):
        output_path.write_bytes(b"partial")
        if "bestaudio" in format_selector:
            raise RuntimeError("audio download failed")
        return output_path


class FailingAudioYoutubeClient:
    def get_title(self, url):
        return "sample"

    def download(self, url, format_selector, output_path):
        output_path.write_bytes(b"partial")
        return output_path


class FailingMediaProcessor:
    def convert_to_mp3(self, audio_path, output_path):
        output_path.write_bytes(b"partial mp3")
        raise RuntimeError("conversion failed")


def test_best_quality_failure_cleans_up_downloaded_temp_files(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    service = DownloadService(
        youtube_client=FailingBestYoutubeClient(),
        media_processor=FailingMediaProcessor(),
    )

    with pytest.raises(RuntimeError, match="audio download failed"):
        service.download(DownloadRequest(url="https://example.com/video", quality=Quality.BEST))

    assert not Path("sample_video.mp4").exists()
    assert not Path("sample_audio.mp4").exists()


def test_audio_only_failure_cleans_up_intermediate_files(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    service = DownloadService(
        youtube_client=FailingAudioYoutubeClient(),
        media_processor=FailingMediaProcessor(),
    )

    with pytest.raises(RuntimeError, match="conversion failed"):
        service.download(
            DownloadRequest(url="https://example.com/video", quality=Quality.AUDIO_ONLY)
        )

    assert not Path("sample_audio.mp4").exists()
    assert not Path("sample.mp3").exists()
