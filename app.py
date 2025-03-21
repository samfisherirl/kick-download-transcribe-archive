import required.firefox_linkgrabber as firefox_linkgrabber
import required.log_manager as log_manager
import required.stable_whisper_handler as stable_whisper_handler
import required.ytdlp as ytdlp
import required.transcription_handler as transcription_handler
import required.file_management as file_management
import required.handbrake_cli as handbrake_cli
import required.rumble_handler as rumble_handler
from pathlib import Path


class VODProcessor:
    def __init__(self, channel, firefox_path, **params):
        self.channel = channel
        self.firefox_path = firefox_path
        self.log_manager = log_manager.LogManager(project_name=f"{channel}_VODDownloader")
        self.transcriber = stable_whisper_handler.Transcriber(log_manager=self.log_manager)
        self.delete_video_when_done = params.get('delete_video_when_done', False)
        self.open_log_when_done = params.get('open_log_when_done', True)
        self.monitor = params.get('monitor', True)
        self.headless_browser = params.get('headless_browser', False)

    def get_vods(self):
        # Retrieve VODs using Firefox link grabber
        return firefox_linkgrabber.run(self.channel, self.firefox_path, self.headless_browser)

    def download_vod(self, vod):
        # Download VOD using youtube-dl
        vod_id = vod.split("/")[-1]
        download_path = Path(self.log_manager.base_dir) / vod_id
        self.log_manager.log_vod_download(vod)
        return ytdlp.download_video(vod, str(download_path))

    def compress_vod(self, file_path):
        """Compress VOD using Handbrake CLI"""
        cleaned_path = file_management.clean_path(file_path)
        converter = handbrake_cli.HandbrakeConverter()
        return converter.convert_video(cleaned_path)

    def transcribe_vod(self, vod_path, v_id):
        return transcription_handler.transcribe_video(vod_path, v_id)

    def run(self, only_latest=True):
        vods = self.get_vods()
        downloaded_vods = self.log_manager.get_downloaded_vods()
        undownloaded_vods = self.log_manager.filter_undownloaded_vods(vods)
        for vod in undownloaded_vods:
            downloaded_file = self.download_vod(vod)
            if downloaded_file:
                v_id = vod.split("/")[-1]
                compressed_vod = self.compress_vod(downloaded_file)
                transcription = self.transcribe_vod(compressed_vod, v_id)
                if transcription:
                    print(f"Transcription for VOD {v_id}: {transcription}")
                if self.delete_video_when_done:
                    file_management.delete_file(compressed_vod)  # Delete video if option is selected
                if only_latest:
                    break


if __name__ == "__main__":

    ## test
    ## test

    firefox_executable_path = r"D:\Documents\FirefoxPortable\App\Firefox64\firefox.exe"
    vod_processor = VODProcessor(channel="jstlk", firefox_path=firefox_executable_path)
    vod_processor.run()
