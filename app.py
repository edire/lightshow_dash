#%%

from flask import Flask, request, render_template, flash, redirect, url_for, jsonify
import subprocess
import threading
import time
import os
import json
import datetime
from demail.gmail import SendEmail
import datetime as dt


app = Flask(__name__)
app.secret_key = os.urandom(24)

song_queue_requested = []
song_queue_system = []
os.environ['SYNCHRONIZED_LIGHTS_HOME']='/home/pi/lightshowpi'
current_song = None


#%%

def get_song_list():
    with open('songs.json') as f:
        songs = json.load(f)
    songs = dict(sorted(songs.items()))
    return songs


def check_time():
    current_time = datetime.datetime.now().time()
    start_time = datetime.time(17, 30)
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
    command = ["sudo", "python3.7", "/home/pi/lightshowpi/py/synchronized_lights.py", f"--file=/home/pi/lightshowpi/music/christmas/{song_name}.mp3"]
    subprocess.call(command)
    lights_on()
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
        with open('song_requests.txt', 'a') as f:
            timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - {selected_song}\n")
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


@app.route('/cancel', methods=['GET'])
def cancel_song():
    command = ["sudo", "pkill", "python3.7"]
    subprocess.call(command)
    return 'done!'


@app.route('/request', methods=['POST'])
def request_song():
    song_request = request.form['song_request']
    if song_request.strip():
        SendEmail(to_email_addresses=os.getenv('EMAIL_ADDRESS')
                , subject=f'LightshowPi Song Request'
                , body=song_request
                , user=os.getenv('EMAIL_UID')
                , password=os.getenv('EMAIL_PWD')
        )
        flash(f"Your request, {song_request}, has been submitted.  Please check back later.")
    return redirect(url_for('index'))


@app.route('/on', methods=['GET'])
def lights_on():
    command = ["sudo", "python3.7", "/home/pi/lightshowpi/py/hardware_controller.py", "--state=on"]
    subprocess.call(command)
    return 'done!'


@app.route('/off', methods=['GET'])
def lights_off():
    command = ["sudo", "python3.7", "/home/pi/lightshowpi/py/hardware_controller.py", "--state=off"]
    subprocess.call(command)
    return 'done!'


@app.route('/git_pull', methods=['GET'])
def git_pull():
    global songs
    command = ["git", "pull"]
    subprocess.call(command)
    songs = get_song_list()
    return 'done!'


#%%

if __name__ == '__main__':
    songs = get_song_list()
    threading.Thread(target=loop_songs, daemon=True).start()
    app.run(debug=False, host='127.0.0.1', port=5000)


#%%
