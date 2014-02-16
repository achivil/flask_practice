import requests

def test():
    payload = {'client_id': '0b5405e19c58e4cc21fc11a4d50aae64',
            'client_secret': 'edfc4e395ef93375',
            'redirect_uri': 'https://www.example.com/back'
            'grant_type' = 'authorization_code'
            'code': '9b73a4248'}
    url = "https://www.douban.com/service/auth2/token"
    r = requests.post(url, data=payload)
    print r.url
    print r.text

if __name__ == "__main__":
    test()
