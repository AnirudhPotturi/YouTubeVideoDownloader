from pathlib import Path
import os

import pytest

from downloader.models import DownloadRequest, Quality
from downloader.service import DownloadService


@pytest.fixture
def integration_url():
    url = os.environ.get("YOUTUBE_INTEGRATION_URL")
    if not url:
        pytest.skip("Set YOUTUBE_INTEGRATION_URL to run integration tests.")
    return url


@pytest.mark.integration
def test_metadata_lookup_uses_live_youtube(integration_url):
    title = DownloadService().youtube_client.get_title(integration_url)

    assert title


@pytest.mark.integration
def test_audio_only_download_creates_mp3(integration_url, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    result = DownloadService().download(
        DownloadRequest(url=integration_url, quality=Quality.AUDIO_ONLY)
    )

    assert result.output_path == Path(f"{result.title}.mp3")
    assert result.output_path.is_file()
    assert result.output_path.stat().st_size > 0
    assert not Path(f"{result.title}_audio.mp4").exists()