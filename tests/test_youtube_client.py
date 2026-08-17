import pytest
from yt_dlp.utils import DownloadError

from downloader.youtube_client import DOWNLOAD_RETRIES, YouTubeClient


class FakeYoutubeDL:
    last_options = None
    error = None

    def __init__(self, options):
        type(self).last_options = options

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def download(self, urls):
        if type(self).error is not None:
            raise type(self).error


@pytest.fixture(autouse=True)
def clear_environment(monkeypatch):
    monkeypatch.delenv("YTDLP_COOKIES_FILE", raising=False)
    monkeypatch.delenv("YTDLP_COOKIES_FROM_BROWSER", raising=False)


def test_download_uses_cookie_file_and_bounded_retries(monkeypatch, tmp_path):
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    monkeypatch.setenv("YTDLP_COOKIES_FILE", str(cookie_file))
    monkeypatch.setenv("YTDLP_COOKIES_FROM_BROWSER", "edge")
    monkeypatch.setattr("downloader.youtube_client.YoutubeDL", FakeYoutubeDL)

    result = YouTubeClient().download(
        "https://example.com/video", "best", tmp_path / "output.mp4"
    )

    assert result == tmp_path / "output.mp4"
    assert FakeYoutubeDL.last_options["cookiefile"] == str(cookie_file)
    assert "cookiesfrombrowser" not in FakeYoutubeDL.last_options
    assert FakeYoutubeDL.last_options["retries"] == DOWNLOAD_RETRIES
    assert FakeYoutubeDL.last_options["fragment_retries"] == DOWNLOAD_RETRIES
    assert FakeYoutubeDL.last_options["extractor_retries"] == DOWNLOAD_RETRIES
    assert FakeYoutubeDL.last_options["file_access_retries"] == DOWNLOAD_RETRIES


@pytest.mark.parametrize(
    ("cookie_contents", "expected_message"),
    [
        ('{"cookies":[]}', "not a valid Netscape-format cookies.txt file"),
        ("example.com\tTRUE\t/\tFALSE\n", "not a valid Netscape-format cookies.txt file"),
        (
            "youtube.com\tTRUE\t/\tFALSE\t0\tSID\tvalue\n"
            "example.com\tTRUE\t/\tFALSE\n",
            "not a valid Netscape-format cookies.txt file",
        ),
    ],
)
def test_invalid_cookie_file_is_reported_before_download(
    monkeypatch, tmp_path, cookie_contents, expected_message
):
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text(cookie_contents, encoding="utf-8")
    monkeypatch.setenv("YTDLP_COOKIES_FILE", str(cookie_file))
    monkeypatch.setattr("downloader.youtube_client.YoutubeDL", FakeYoutubeDL)

    with pytest.raises(RuntimeError, match=expected_message):
        YouTubeClient().download("https://example.com/video", "best", tmp_path / "output.mp4")


def test_missing_cookie_file_is_reported_before_download(monkeypatch, tmp_path):
    monkeypatch.setenv("YTDLP_COOKIES_FILE", str(tmp_path / "missing-cookies.txt"))
    monkeypatch.setattr("downloader.youtube_client.YoutubeDL", FakeYoutubeDL)

    with pytest.raises(RuntimeError, match="was not found or is not a file"):
        YouTubeClient().download("https://example.com/video", "best", tmp_path / "output.mp4")


@pytest.mark.parametrize(
    ("download_error", "expected_message"),
    [
        (
            "ERROR: unable to download video data: HTTP Error 403: Forbidden",
            "YouTube rejected access to this video's media stream",
        ),
        (
            "ERROR: Could not copy Chrome cookie database",
            "browser cookie database is locked",
        ),
        (
            "ERROR: Requested format is not available",
            "selected media format is not currently available",
        ),
        (
            "ERROR: timed out",
            "network or YouTube connectivity problem",
        ),
    ],
)
def test_download_errors_are_reported_with_specific_messages(
    monkeypatch, tmp_path, download_error, expected_message
):
    monkeypatch.setattr("downloader.youtube_client.YoutubeDL", FakeYoutubeDL)
    monkeypatch.setenv("YTDLP_COOKIES_FROM_BROWSER", "edge")
    FakeYoutubeDL.error = DownloadError(download_error)
    output_path = tmp_path / "output.mp4"
    output_path.write_bytes(b"partial")
    (tmp_path / "output.m4a").write_bytes(b"partial")
    (tmp_path / "output.m4a.part").write_bytes(b"partial")

    with pytest.raises(RuntimeError, match=expected_message):
        YouTubeClient().download("https://example.com/video", "best", output_path)

    assert not output_path.exists()
    assert not (tmp_path / "output.m4a").exists()
    assert not (tmp_path / "output.m4a.part").exists()
    FakeYoutubeDL.error = None
