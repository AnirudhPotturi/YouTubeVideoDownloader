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


@pytest.fixture
def restricted_integration_url():
    url = os.environ.get("YOUTUBE_RESTRICTED_INTEGRATION_URL")
    if not url:
        pytest.skip("Set YOUTUBE_RESTRICTED_INTEGRATION_URL to run restricted integration tests.")
    return url


@pytest.fixture
def integration_cookie_file():
    cookie_file = os.environ.get("YTDLP_COOKIES_FILE")
    if not cookie_file:
        pytest.skip("Set YTDLP_COOKIES_FILE to run restricted integration tests.")

    cookie_path = Path(cookie_file).expanduser()
    if not cookie_path.is_file():
        pytest.skip("YTDLP_COOKIES_FILE must point to a local Netscape-format cookies.txt file.")
    return cookie_path


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


@pytest.mark.integration
def test_restricted_audio_only_download_supports_cookie_file(
    restricted_integration_url, integration_cookie_file, monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)

    result = DownloadService().download(
        DownloadRequest(url=restricted_integration_url, quality=Quality.AUDIO_ONLY)
    )

    assert result.output_path == Path(f"{result.title}.mp3")
    assert result.output_path.is_file()
    assert result.output_path.stat().st_size > 0
