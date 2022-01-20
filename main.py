import os
import time
import asyncio
import random

import pause
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

from autonationstates import NationStates


ns = NationStates(os.getenv('NATION'), os.getenv('PASSWORD'))

def answer_all_issues():
    """Gets all available issues in the nation, randomly choose an option,
    write a dispatch about said option, and select choice"""
    issues = ns.get_issues()
    for issue in issues:
        choice = random.randint(0,issues[issue]-1)
        issueinfo = ns.issue_info(issue)
        if issueinfo is None:
            continue
        title = f"Issue {issue}: {issueinfo.find('TITLE').text}"
        text = f"""{issueinfo.find('TEXT').text}
        
        {ns.nation} answered with choice {choice+1}:
        {list(issueinfo.find_all('OPTION'))[choice]}"""
        ns.answer_issue(issue, choice)
        ns.write_dispatch(title, text)


async def issue_loop():
    """Waits for next issue then answers issues"""
    while True:
        answer_all_issues()
        nextissue = ns.get_next_issue_time()
        pause.until(nextissue)

asyncio.run(issue_loop())