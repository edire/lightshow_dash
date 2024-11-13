#%%

from flask import Flask, request, render_template, flash, redirect, url_for, jsonify
import subprocess
import threading
import time
import os
import json
import datetime


app = Flask(__name__)
app.secret_key = os.urandom(24)

song_queue_requested = []
song_queue_system = []
os.environ['SYNCHRONIZED_LIGHTS_HOME']='/home/pi/lightshowpi'
current_song = None


with open('songs.json') as f:
    songs = json.load(f)
songs = dict(sorted(songs.items()))

#%%

def check_time():
    current_time = datetime.datetime.now().time()
    start_time = datetime.time(1, 0)
    end_time = datetime.time(20, 35)
    if start_time <= current_time <= end_time:
        return True
    else:
        return False

def add_song_to_queue(song_queue, song_name):
    song_queue.append(song_name)
    return "Song added to queue: " + song_name


def play_song(song_name):
    print("Playing:", song_name)
    song_name = songs[song_name]
    command = ["python", "/home/pi/lightshowpi/py/synchronized_lights.py", f"--file=/home/pi/lightshowpi/music/christmas/{song_name}.mp3"]
    subprocess.call(command)
    # print(command)
    # time.sleep(10)


def loop_songs():
    global current_song
    while True:
        if song_queue_requested:
            current_song = song_queue_requested.pop(0)
        elif song_queue_system:
            current_song = song_queue_system.pop(0)
        if check_time() and current_song:
            play_song(current_song)
            current_song = None
        else:
            time.sleep(2)


#%%

@app.route('/')
def index():
    return render_template('index.html', songs=songs, song_queue_requested = song_queue_requested, song_queue_system = song_queue_system)


@app.route('/choose_song', methods=['POST'])
def choose_song():
    selected_song = request.form.get('song')
    if not selected_song:
        flash("No song selected. Please choose a song.")
        return redirect(url_for('index'))
    if check_time():
        add_song_to_queue(song_queue_requested, selected_song)
        flash(f"Your song '{selected_song}' has been added to the queue!")
    else:
        flash("Current time is outside the allowed range of 5:30p - 8:30p. Song will not be played at this time.")
    return redirect(url_for('index'))


@app.route('/play', methods=['POST'])
def add_song_webhook():
    data = request.get_json()
    song_name = data.get('song_name') if data else None
    if song_name:
        add_song_to_queue(song_queue_system, song_name)
        return jsonify({"message": "Song added to queue: " + song_name}), 200
    else:
        return jsonify({"message": "No song provided in request."}), 400


@app.route('/current_song', methods=['GET'])
def get_current_song():
    return current_song if current_song else "No song currently playing."


#%%

if __name__ == '__main__':
    threading.Thread(target=loop_songs, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)


#%%
