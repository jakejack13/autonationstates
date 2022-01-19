import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


BASEURL = 'https://www.nationstates.net/cgi-bin/api.cgi'
USERAGENT = 'github.com/jakejack13'
REAUTHCODE = 403

class AuthenticationError(Exception):
    pass

class NationStates:

    nation: str
    _autologin: str
    _pin: str

    def __init__(self, nation: str, password: str) -> None:
        self.nation = nation
        self._first_auth(password)


    def _create_shard_response(self, shard: str) -> requests.Response:
        params = {'nation': self.nation, 'q': shard}
        headers = {'X-Pin': self.pin, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        if r.status_code == REAUTHCODE:
            self.ping()
            r = self._create_shard_response(shard)
        return r
    

    def _first_auth(self, password):
        params = {'nation': self.nation, 'q': 'ping'}
        headers = {'X-Password': password, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        self.autologin = r.headers['X-autologin']
        self.pin = r.headers['X-pin']
        

    def ping(self) -> None:
        params = {'nation': self.nation, 'q': 'ping'}
        headers = {'X-Autologin': self.autologin, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        if r.status_code != 200:
            raise AuthenticationError('Nation failed to log in with supplied password')
        self.pin = r.headers['X-pin']


    def get_issues(self) -> dict[str, int]:
        r = self._create_shard_response('issues')
        soup = BeautifulSoup(r.text, 'xml')
        issues: dict[str, int]= {}
        for tag in soup.find_all('ISSUE'):
            tag: Tag
            issues[tag['id']] = len(tag.find_all('OPTION'))
        return issues

    def answer_issue(self, issue_id, choice) -> bool:
        params = {'nation': self.nation, 'c': 'issue', 'issue': issue_id, 'option': choice}
        headers = {'X-Pin': self.pin, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        return r.status_code == 200