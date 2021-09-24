import requests
import sys
import os
import time
from urllib.parse import urlencode
from dotenv import load_dotenv
load_dotenv()

env_values = [
    "VACCINE_RESERVATION_URL", "VACCINE_ALL_PLACE_URL",
    "VACCINE_AVAILABLE_PLACE_URL", "LINE_TOKEN_FILE_PATH", "NOTIFY_DURATION_SEC"
]

# Check values
for key in env_values:
    value = os.environ.get(key)
    if not value:
        print("OS env value is not found: " + key)
        sys.exit(1)
    print(key + ": " + value)

l_notify_url = "https://notify-api.line.me/api/notify"
l_cancel_url = "https://notify-bot.line.me/my/"
r_url = os.environ.get("VACCINE_RESERVATION_URL")
v_places_url = os.environ.get("VACCINE_ALL_PLACE_URL")
v_ava_places_url = os.environ.get("VACCINE_AVAILABLE_PLACE_URL")
token_file_path = os.environ.get("LINE_TOKEN_FILE_PATH")
duration = int(os.environ.get("NOTIFY_DURATION_SEC"))


class Vaccine:
    def __init__(self):
        # Get all places
        r = requests.get(v_places_url)
        if r.status_code != 200:
            sys.exit(1)
        self.places = r.json()['department']
        self.ava_places_prev = []

    def get_available_place_ids(self):
        r = requests.get(v_ava_places_url)
        if r.status_code != 200:
            return None

        ava_place_ids = r.json()["department_list"]
        if len(ava_place_ids) == 0:
            return None

        return ava_place_ids

    def get_available_places(self):
        ava_place_ids = self.get_available_place_ids()
        if ava_place_ids == None:
            print("No available place...")
            return None

        ava_places = []
        for target_id in ava_place_ids:
            for place in self.places:
                place_id = place["id"]
                if place_id == target_id:
                    place_name = place["name"]
                    ava_places.append(place_name)
                    break
        print(ava_places)
        return ava_places

    def notify_available_places(self):
        ava_places = self.get_available_places()
        if ava_places == None:
            return

        self.ava_places_prev = ava_places
        msg_place = '\n'.join(ava_places)
        msg = "\n" + msg_place + "\n\n<Reservation URL(予約サイト)>\n" + r_url + "\n<Cancel Notify(通知解除)>\n" + l_cancel_url
        self.notify_line(msg)

    def notify_line(self, msg):
        print("Trying to notify")
        if not os.path.isfile(token_file_path):
            return 
        
        invalid_tokens = []
        with open(token_file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                access_token = line.rstrip()
                params = {
                    'message': msg,
                }
                params = urlencode(params)
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Bearer ' + access_token.rstrip()
                }
                r = requests.post(url=l_notify_url,
                                  data=params,
                                  headers=headers)
                if r.status_code == 401:
                    invalid_tokens.append(line)
                elif r.status_code != 200:
                    print(r)
        print("LINE notification has been done")

        # Remove invalid tokens
        if len(invalid_tokens) > 0 :
            print("Trying to delete invalid tokens")
            with open(token_file_path, 'w') as f:
                for line in lines:
                    if line not in invalid_tokens:
                        f.write(line)
            print("Delete invalid token has been done")



def main():
    v = Vaccine()
    while True:
        v.notify_available_places()
        time.sleep(duration)


if __name__ == "__main__":
    main()
