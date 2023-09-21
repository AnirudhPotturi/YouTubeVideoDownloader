# YouTube Video Downloader

The YouTube downloader application utilizes the Pytube module to fetch and download videos from Youtube. The application provides two options for downloading. The standard option can be used to download videos with the highest resolution that the module can process. Most of the times, this happens to be capped at 720p.

The pytube module offers a feature to download videos at higher resolutions like 1080p except with no audio. The second option this application offers allows you to download videos available at the highest resolutions. We download the audio and video files separately and use the Moviepy module to stitch the audio and video files together. 

## Instructions 
Install required modules with the following command:

pip install -r requirements.txt

Next, use the following command to run the application:

python main.py