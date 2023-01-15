"""The runner for autonationstates

@author Jacob Kerr"""

import os
import asyncio
import random

import pause
from dotenv import load_dotenv
load_dotenv()

from autonationstates import NationStates


ns = NationStates(os.getenv('NATION'), os.getenv('PASSWORD'))

def answer_all_issues():
    """Gets all available issues in the nation, randomly choose an option,
    write a dispatch about said option, and select choice"""
    issues = ns.get_issues()
    print("Issues: ")
    print([issue for issue in issues])
    for issue in issues:
        choice = random.randint(0,issues[issue]-1)
        issueinfo = ns.issue_info(issue)
        if issueinfo is None:
            continue
        title = f"Issue {issue}: {issueinfo.find('TITLE').text}"
        text = f"""{issueinfo.find('TEXT').text}
        
        {ns.nation} answered with choice {choice+1}:
        {list(issueinfo.find_all('OPTION'))[choice]}"""
        success = ns.answer_issue(issue, choice)
        if success:
            print(f"Answered issue {issue} with choice {choice}")
        else:
            print(f"Failed to answer {issue}")
        success = ns.write_dispatch(title, text)
        if success:
            print(f"Wrote dispatch with title {title}")
        else:
            print(f"Failed to write dispath with title {title}")


async def issue_loop():
    """Waits for next issue then answers issues"""
    while True:
        answer_all_issues()
        nextissue = ns.get_next_issue_time()
        pause.until(nextissue)

print(f"Logged in as nation {ns.nation}")
asyncio.run(issue_loop())
