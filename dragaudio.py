import tkinter as tk
import yt_dlp
import os
import threading
import re
from pydub import AudioSegment
import configparser

class DragAudio:
    def __init__(self):
        self.url_list = []
        self.download_thread = threading.Thread(target=self.download_songs)
        self.load_settings()
        self.create_ui()

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('./settings.conf')
        self.download_dir = os.path.expanduser(config.get('Paths', 'path', fallback=config.get('DEFAULT', 'path')))
        self.foreground = config.get('Colors', 'foreground', fallback=config.get('DEFAULT', 'foreground'))
        self.background = config.get('Colors', 'background', fallback=config.get('DEFAULT', 'background'))

    def create_ui(self):
        self.root = tk.Tk()
        self.root.title("DragAudio")
        self.root.configure(bg=self.background)
        self.root.resizable(False, False)

        self.label = tk.Label(self.root, text="Specify song URL:", bg=self.background, fg=self.foreground)
        self.label.pack(padx=4, pady=4)

        self.entry = tk.Entry(self.root, bg=self.foreground, fg=self.background)
        self.entry.pack(padx=4, pady=4)

        self.button = tk.Button(self.root, text="Download", command=self.add_url, bg=self.foreground, fg=self.background)
        self.button.pack(padx=4, pady=4)

    def add_url(self):
        url = self.entry.get()
        if url:
            urls = [u.strip() for u in re.split(r'[ ,;\n]+', url) if u.strip()]
            self.url_list.extend(urls)
            self.entry.delete(0, tk.END)
            if not self.download_thread.is_alive():
                self.start_download_thread()

    def start_download_thread(self):
        self.download_thread = threading.Thread(target=self.download_songs)
        self.download_thread.start()

    def download_songs(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
                'preferredquality': '0',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            while self.url_list:

                # Step 1 - download
                url = self.url_list.pop(0)
                info_dict = ydl.extract_info(url, download=True)
                audio_file = ydl.prepare_filename(info_dict).replace('.opus', '.flac')
                print(f"Downloaded {audio_file}")
                
                # Step 2 - normalization
                audio = AudioSegment.from_file(audio_file)
                normalized_audio = audio.normalize()
                normalized_audio.export(audio_file, format="flac")
                print(f"Normalized {audio_file}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    DragAudio().run()
