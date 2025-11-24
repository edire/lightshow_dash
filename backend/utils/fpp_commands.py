
import time


is_prod = False


if is_prod:

    import os
    import requests


    FPP_IP = os.getenv('FPP_IP')
    FPP_UID = os.getenv('FPP_UID')
    FPP_PWD = os.getenv('FPP_PWD')


    def play_song(song_file):
        print("Playing:", song_file)
        url = f'http://{FPP_IP}/api/playlist/{song_file}/start'
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
        url = f'http://{FPP_IP}/api/playlists/stop'
        requests.get(url, auth=(FPP_UID, FPP_PWD))


    def lights_on():
        url = f'http://{FPP_IP}/api/lights/on'
        requests.get(url, auth=(FPP_UID, FPP_PWD))


    def lights_off():
        url = f'http://{FPP_IP}/api/lights/off'
        requests.get(url, auth=(FPP_UID, FPP_PWD))

else:
    
    def play_song(song_file):
        print("Playing (dev mode):", song_file)
        time.sleep(15)  # Simulate song duration


    def is_busy():
        return False


    def stop_song():
        print("Stopping song (dev mode)")


    def lights_on():
        print("Lights ON (dev mode)")


    def lights_off():
        print("Lights OFF (dev mode)")