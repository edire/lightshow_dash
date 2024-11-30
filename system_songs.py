
import os
import requests
import json
import random
import datetime as dt


directory = os.path.dirname(os.path.abspath(__file__))

def add_song_to_queue(song_name):
    if song_name not in songs:
        print(f"Song '{song_name}' not found in the database.")
        return
    url = 'http://localhost:5000/play'
    payload = {'song_name': song_name}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(response.json()['message'])
    else:
        print(response.json()['message'])


def get_list():
    dt_stamp = dt.datetime.now().strftime('%Y%m%d')
    filepath_playlist = os.path.join(directory, 'playlist.json')
    with open(filepath_playlist, 'r') as f:
        playlist = json.load(f)
    if playlist['dt_stamp'] != dt_stamp:
        playlist = {}
        playlist['dt_stamp'] = dt_stamp
        with open(os.path.join(directory, 'songs.json'), 'r') as f:
            songs = json.load(f)
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
    songs = get_list()
    for song in songs:
        add_song_to_queue(song)