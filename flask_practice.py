from flask import Flask
from flask import render_template, redirect, request, make_response
from flask import g
from pymongo import MongoClient
import requests
import json
import urllib
from douban_client import DoubanClient

API_KEY = '0b99fc3f44a14d4622cdf4bdcde3e7d2'
API_SECRET = '5f050ac891289c81'
SCOPE = 'douban_basic_common,shuo_basic_r,shuo_basic_w'
client = DoubanClient(API_KEY, API_SECRET, 'http://localhost:5000/back', SCOPE)

app = Flask(__name__)
client = MongoClient(max_pool_size=100, w=0, auto_start_request=True)
dbname = client.flask_practice

@app.before_request
def before_request():
    g.db = client.start_request()

@app.after_request
def after_request(response):
    g.db.end()
    return response

@app.route('/get_access_token', methods=['GET', 'POST'])
def get_authorization_code():
    url = "https://www.douban.com/service/auth2/auth?" \
          "client_id=0b99fc3f44a14d4622cdf4bdcde3e7d2&" \
          "redirect_uri=http://localhost:5000/back&" \
          "response_type=token&" \
          "scope=shuo_basic_r,shuo_basic_w,douban_basic_common"
    info = requests.get(url)
    print info.text
    return info.text


def get_user_info_from_douban(douban_name):
    url = "http://api.douban.com/v2/user?q=" + douban_name
    info = requests.get(url)
    return info.text

def get_user_bubs_from_douban(douban_uid):
    url = "http://api.douban.com/labs/bubbler/" + douban_uid + "/irachex/bubs"
    info = requests.get(url)
    return info.text

@app.route('/', methods=['GET', 'POST'])
def index():
    user_info = {}
    authorization_code_url = "https://www.douban.com/service/auth2/auth?" \
                             "client_id=0b99fc3f44a14d4622cdf4bdcde3e7d2&" \
                             "redirect_uri=http://localhost:5000/back&" \
                             "response_type=code&" \
                             "scope=shuo_basic_r,shuo_basic_w,douban_basic_common"
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        search_result = json.loads(get_user_info_from_douban(request.form['username']))
        print search_result['users']
        users = search_result['users']
        for u in users:
            if u['name'] == request.form['username']:
                user_info = u
                break
        if user_info:
            user_site = user_info['alt']
            user_page = requests.get(user_site)
            return make_response(user_page.text)

    return render_template("index.html", info=user_info, author_url=authorization_code_url)

@app.route('/back', methods=['GET', 'POST'])
def api_back():
    print request
    try:
        authorization_code = request.args.get('code', 'error')
        print authorization_code
        payload = {'client_id': '0b99fc3f44a14d4622cdf4bdcde3e7d2',
                'client_secret': '5f050ac891289c81',
                'redirect_uri': 'http://localhost:5000/back',
                'grant_type': 'authorization_code',
                'code': authorization_code}
        result = requests.post("https://www.douban.com/service/auth2/token", data=payload)
        access_info = json.loads(result.text)
        print "access_token back: "
        print access_info["access_token"]
        headers = {'Authorization': 'Bearer '+access_info['access_token']}
        result = requests.get("https://api.douban.com/v2/user/~me", headers=headers)
        return make_response(result.text)
    except:
        pass
    return make_response('200')



if __name__ == '__main__':
    app.run(debug=True)
