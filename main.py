import DownloadRunner as dr

print("Enter quality of video \n1. Standard (max 720p)\n2. Best available resolution\n3. Audio only")

quality = input()

print("Paste the link of your video:\t")

youtubeLink = input()

dr.runner(youtubeLink, quality)

if int(quality) <= 2 :
    print('Your video has been downloaded!')
else:
    print('Your audio has been downloaded!')