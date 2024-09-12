from pathlib import Path

import os
import re
import httpretty

from httpretty import httprettified
from cbibs.cbibs import CbibsModule

user_agent_format = re.compile(r'^opencage-python/[\d.]+ Python/[\d.]+ (requests)/[\d.]+$')

cbibs = CbibsModule('abc')

