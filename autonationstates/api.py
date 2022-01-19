import requests

BASEURL = 'https://www.nationstates.net/cgi-bin/api.cgi'
USERAGENT = 'github.com/jakejack13'
REAUTHCODE = 403


class NationStates:

    nation: str
    _autologin: str
    _pin: str

    def __init__(self, nation, password):
        self.nation = nation
        self._first_auth(password)
    

    def _first_auth(self, password):
        params = {'nation': self.nation, 'q': 'ping'}
        headers = {'X-Password': password, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        self.autologin = r.headers['X-autologin']
        self.pin = r.headers['X-pin']
        

    def ping(self):
        params = {'nation': self.nation, 'q': 'ping'}
        headers = {'X-Autologin': self.autologin, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        self.pin = r.headers['X-pin']

