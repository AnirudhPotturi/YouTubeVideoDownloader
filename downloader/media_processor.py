from pathlib import Path

from moviepy.editor import AudioFileClip, VideoFileClip


class MediaProcessor:
    def stitch(self, video_path: Path, audio_path: Path, output_path: Path) -> Path:
        with VideoFileClip(str(video_path)) as video_clip, AudioFileClip(str(audio_path)) as audio_clip:
            final_clip = video_clip.set_audio(audio_clip)
            try:
                final_clip.write_videofile(str(output_path))
            finally:
                final_clip.close()
        audio_path.unlink()
        video_path.unlink()
        return output_path

    def convert_to_mp3(self, audio_path: Path, output_path: Path) -> Path:
        with AudioFileClip(str(audio_path)) as audio_clip:
            audio_clip.write_audiofile(str(output_path))
        audio_path.unlink()
        return output_path