"""The wrapper for the NationStates API that allows control of nations

@author Jacob Kerr"""

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
        """Creates a new NationStates API wrapper with nation `nation` and password `password`"""
        self.nation = nation
        self._first_auth(password)


    def _create_shard_response(self, shard: str) -> requests.Response:
        """Creates a new shard response for shard `shard`"""
        params = {'nation': self.nation, 'q': shard}
        headers = {'X-Pin': self.pin, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        if r.status_code == REAUTHCODE:
            self.ping()
            r = self._create_shard_response(shard)
        return r
    

    def _first_auth(self, password: str):
        """Uses the given password `password` to authenticate with NS and
        generate an autologin and pin"""
        params = {'nation': self.nation, 'q': 'ping'}
        headers = {'X-Password': password, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        self.autologin = r.headers['X-autologin']
        self.pin = r.headers['X-pin']
        

    def ping(self) -> None:
        """Pings NS and refreshes the pin"""
        params = {'nation': self.nation, 'q': 'ping'}
        headers = {'X-Autologin': self.autologin, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        if r.status_code != 200:
            raise AuthenticationError('Nation failed to log in with supplied password')
        self.pin = r.headers['X-pin']


    def get_issues(self) -> dict[str, int]:
        """Returns the issue id/number of options pairs for the given account"""
        r = self._create_shard_response('issues')
        soup = BeautifulSoup(r.text, 'xml')
        issues: dict[str, int]= {}
        for tag in soup.find_all('ISSUE'):
            tag: Tag
            issues[tag['id']] = len(tag.find_all('OPTION'))
        return issues


    def issue_info(self, issue_id: str) -> Tag | None:
        """Returns the parsed XML info of the issue with issue id `issue_id` or
        `None` if this issue is not found"""
        r = self._create_shard_response('issues')
        soup = BeautifulSoup(r.text, 'xml')
        for tag in soup.find_all('ISSUE'):
            tag: Tag
            if tag['id'] == issue_id:
                return tag
        return None


    def answer_issue(self, issue_id: str, choice: int) -> bool:
        """Answers the issue of id `issue_id` with choice number `choice` and
        returns `True` if successful"""
        params = {'nation': self.nation, 'c': 'issue', 'issue': issue_id, 'option': choice}
        headers = {'X-Pin': self.pin, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        if r.status_code == REAUTHCODE:
            self.ping()
            return self.answer_issue(issue_id, choice)
        return r.status_code == 200


    def get_next_issue_time(self) -> int:
        """Returns the time until the next issue in seconds from the epoch"""
        r = self._create_shard_response('nextissuetime')
        soup = BeautifulSoup(r.text, 'xml')
        return int(soup.find('NEXTISSUETIME').text)


    def write_dispatch(self, title: str, text: str, category: int = 1, subcategory: int = 100) -> bool:
        """Writes a dispatch with title `title`, text `text`, category
        `category`, and subcategory `subcategory` and returns `True` if successful"""
        params = {'nation': self.nation, 'c': 'dispatch', 'dispatch': 'add',
            'title': title, 'text': text, 'category': category, 
            'subcategory': subcategory, 'mode': 'prepare'
        }
        headers = {'X-Pin': self.pin, 'User-Agent': USERAGENT}
        r = requests.get(BASEURL, params=params, headers=headers)
        if r.status_code == REAUTHCODE:
            self.ping()
            return self.write_dispatch(self, title, text, category, subcategory)
        soup = BeautifulSoup(r.text, 'xml')
        token = soup.find('SUCCESS').text

        params = {'nation': self.nation, 'c': 'dispatch', 'dispatch': 'add',
            'title': title, 'text': text, 'category': category, 
            'subcategory': subcategory, 'mode': 'execute', 'token': token
        }
        r = requests.get(BASEURL, params=params, headers=headers)
        return r.status_code == 200
