from .models import DownloadRequest, Quality
from .service import DownloadService


MENU = """Enter quality of video
1. Standard (max 720p)
2. Best available resolution
3. Audio only
q - Quit"""


def run():
    service = DownloadService()
    while True:
        print(MENU)
        choice = input().strip().lower()
        if choice == "q":
            return

        try:
            quality = Quality(int(choice))
        except ValueError:
            print("Choose 1, 2, 3, or q.")
            continue

        print("Paste the link of your video:")
        url = input().strip()
        if not url:
            print("A video link is required.")
            continue

        try:
            result = service.download(DownloadRequest(url=url, quality=quality))
        except Exception as error:
            print(f"Download failed: {error}")
            continue

        print(f"Saved to {result.output_path}")