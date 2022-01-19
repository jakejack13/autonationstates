import os
from dotenv import load_dotenv

from autonationstates.api import NationStates

load_dotenv()

ns = NationStates(os.getenv('NATION'), os.getenv('PASSWORD'))
print(ns.get_issues())
