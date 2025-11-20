
import os
import json
import random
import datetime as dt
import utils.queueing as queueing


from app.page_index import song_queue_manager


directory = os.path.dirname(os.path.abspath(__file__))


def get_list(songs):
    dt_stamp = dt.datetime.now().strftime('%Y%m%d')
    filepath_playlist = os.path.join(directory, 'playlist.json')
    with open(filepath_playlist, 'r') as f:
        playlist = json.load(f)
    if playlist['dt_stamp'] != dt_stamp:
        playlist = {}
        playlist['dt_stamp'] = dt_stamp
        song_list = list(songs.keys())
        random_songs = random.sample(song_list, 9)
        playlist['song_list'] = random_songs
        playlist['start'] = 0
        playlist['end'] = 3
    songs = playlist['song_list'][playlist['start']:playlist['end']]
    playlist['start'] += 3
    playlist['end'] += 3
    with open(filepath_playlist, 'w') as f:
        json.dump(playlist, f)
    return songs


if __name__ == "__main__":
    songs = queueing.get_song_list()
    song_list = get_list(songs)
    for song in song_list:
        song_queue_manager.add_song(song, queue_type="system")