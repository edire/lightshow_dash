
import time
import os
import requests


FPP_IP = os.getenv('FPP_IP')
FPP_UID = os.getenv('FPP_UID')
FPP_PWD = os.getenv('FPP_PWD')
IS_DEV = os.getenv('IS_DEV', '1') == '1'


def play_song(song_file):
    print("Playing:", song_file)
    if IS_DEV:
        time.sleep(15)  # Simulate song duration
        return
    lights_off()
    time.sleep(1)
    url = f'http://{FPP_IP}/api/playlist/{song_file}.fseq/start'
    requests.get(url, auth=(FPP_UID, FPP_PWD))
    while is_busy():
        time.sleep(2)
    lights_on()


def is_busy():
    url = f'http://{FPP_IP}/api/fppd/status'
    response = requests.get(url, auth=(FPP_UID, FPP_PWD))
    if response.json()['current_playlist']['playlist'] != "":
        return True
    return False


def stop_song():
    if IS_DEV:
        print("Stopping song (dev mode)")
        return
    url = f'http://{FPP_IP}/api/playlists/stop'
    requests.get(url, auth=(FPP_UID, FPP_PWD))


def lights_on():
    if IS_DEV:
        print("Lights ON (dev mode)")
        return
    # url = f'http://{FPP_IP}/api/command/Start%20Playlist/lights_on/true/true'
    url = f'http://{FPP_IP}/api/command/FSEQ%20Effect%20Start/lights_on/true/true'
    requests.get(url, auth=(FPP_UID, FPP_PWD))


def lights_off():
    if IS_DEV:
        print("Lights OFF (dev mode)")
        return
    url = f'http://{FPP_IP}/api/command/FSEQ%20Effect%20Stop/lights_on'
    requests.get(url, auth=(FPP_UID, FPP_PWD))


# def start_fans():
#     url = f'http://{FPP_IP}/api/command/FSEQ%20Effect%20Start/fans_on/true/true'
#     requests.get(url, auth=(FPP_UID, FPP_PWD))
