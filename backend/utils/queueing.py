
import threading
import json
import time
import datetime
from backend.utils.fpp_commands import play_song


start_time = datetime.time(17, 30)
end_time = datetime.time(20, 35)


def get_song_list():
    with open('songs.json') as f:
        songs = json.load(f)
    songs = dict(sorted(songs.items()))
    return songs


def check_time():
    current_time = datetime.datetime.now().time()
    if start_time <= current_time <= end_time:
        return True
    else:
        return False



class SongQueueManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.admin_queue: list[str] = []
        self.requested_queue: list[str] = []
        self.system_queue: list[str] = []
        self.current_song: str | None = None
        self.song_list = get_song_list()


    def add_song(self, song: str, queue_type: str = "requested"):
        with self.lock:
            if queue_type == "admin":
                self.admin_queue.append(song)
            elif queue_type == "system":
                self.system_queue.append(song)
            else:
                self.requested_queue.append(song)


    def get_next_song(self) -> str | None:
        next_song = None
        with self.lock:
            if self.admin_queue:
                return self.admin_queue.pop(0)
            elif self.requested_queue:
                next_song = self.requested_queue.pop(0)
            elif self.system_queue:
                next_song = self.system_queue.pop(0)
            if next_song and check_time():
                return next_song
            return None


    def peek_queues(self, queue_type: str | None = None):
        with self.lock:
            if queue_type == "admin":
                return self.admin_queue.copy()
            elif queue_type == "requested":
                return self.requested_queue.copy()
            elif queue_type == "system":
                return self.system_queue.copy()
            return None


    def set_current_song(self, song: str):
        with self.lock:
            self.current_song = song


    def get_current_song(self) -> str | None:
        with self.lock:
            return self.current_song
        

    def clear_queues(self):
        with self.lock:
            self.admin_queue.clear()
            self.requested_queue.clear()
            self.system_queue.clear()


    def loop_songs(self):
        songs = get_song_list()
        while True:
            next_song = self.get_next_song()
            if next_song:
                self.set_current_song(next_song)
                song_file = songs[next_song]
                play_song(song_file)
                self.set_current_song(None)
            else:
                time.sleep(2)


# Create a global instance for the application to use
song_queue_manager = SongQueueManager()