
import requests
import json
import random


with open('songs.json') as f:
    songs = json.load(f)


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

# Example usage
if __name__ == "__main__":
    song_list = list(songs.keys())
    random_songs = random.sample(song_list, 3)
    for song in random_songs:
        add_song_to_queue(song)