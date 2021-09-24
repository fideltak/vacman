import requests
import sys
from flask import Flask, redirect, request, render_template_string, abort
import os
from hashlib import sha1
from urllib.parse import urlencode
from dotenv import load_dotenv
load_dotenv()

env_values = [
    "LINE_TOKEN_FILE_PATH", "LINE_NOTIFY_CLIENT_ID", "LINE_NOTIFY_CLIENT_SECRET",
    "LINE_NOTIFY_CALLBACK_URL", "WEB_SERVER_PORT"
]

# Check values
for key in env_values:
    value = os.environ.get(key)
    if not value:
        print("OS env value is not found: " + key)
        sys.exit(1)
    print(key + ": " + value)

# global value
l_auth_url = "https://notify-bot.line.me/oauth/authorize"
l_token_url = "https://notify-bot.line.me/oauth/token"
token_file_path = os.environ.get("LINE_TOKEN_FILE_PATH")
l_id = os.environ.get("LINE_NOTIFY_CLIENT_ID")
l_secret = os.environ.get("LINE_NOTIFY_CLIENT_SECRET")
l_callback_url = os.environ.get("LINE_NOTIFY_CALLBACK_URL")
web_port = os.environ.get("WEB_SERVER_PORT")

class Web:
    def run(self):
        app = Flask(__name__, static_folder='.', static_url_path='')
        csrf_token = sha1(os.urandom(64)).hexdigest()

        @app.route('/line/notify', methods=['GET'])
        def line_notify():
            query = {
                'response_type': 'code',
                'client_id': l_id,
                'redirect_uri': l_callback_url,
                'scope': 'notify',
                'state': csrf_token,
                'response_mode': 'form_post'
            }
            url = l_auth_url + '?' + urlencode(query)
            app.logger.info('Redirect URL: ' + url)
            return redirect(url)

        @app.route('/line/callback', methods=['POST'])
        def line_callback():
            if 'code' in request.form and 'state' in request.form:
                if request.form['state'] != csrf_token:
                    abort(400)

                code = request.form['code']
                params = {
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': l_callback_url,
                    'client_id': l_id,
                    'client_secret': l_secret
                }
                params = urlencode(params)
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                r = requests.post(url=l_token_url,
                                  data=params,
                                  headers=headers)

                app.logger.info(r.json())
                if r.status_code != 200:
                    return render_template_string('Something Wrong:('), 500

                if 'access_token' in r.json():
                    self.save_token(r.json()['access_token'])
                    return render_template_string(
                        'Succeed! Check your Line app!'), 200
                else:
                    return render_template_string(
                        'Failed to get access token from Line:('), 500

            return request.get_data(), 500

        app.run(host='0.0.0.0', port=web_port, debug=True)

    def save_token(self, token_string):
        path = token_file_path
        with open(path, 'a+') as f:
            f.write(token_string + '\n')


def main():
    w = Web()
    w.run()

if __name__ == "__main__":
    main()
