from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path


class Quality(IntEnum):
    STANDARD = 1
    BEST = 2
    AUDIO_ONLY = 3


@dataclass(frozen=True)
class DownloadRequest:
    url: str
    quality: Quality


@dataclass(frozen=True)
class DownloadResult:
    title: str
    output_path: Path