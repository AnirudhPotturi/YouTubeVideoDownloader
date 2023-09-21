import DownloadRunner as dr

print("Enter quality of video \n 1. Standard (max 720p)\n 2. Best available resolution")

quality = input()

print("Paste the link of your video:\t")

youtubeLink = input()

dr.runner(youtubeLink, quality)
print('Your video has been downloaded!')