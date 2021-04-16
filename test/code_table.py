import os
import sys

project_path = os.path.abspath(__file__+'/../..')
if project_path not in sys.path:
    sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from config.sysfiles.parameter import *
from stock.wrapper import CodeWrapper as cw
from trading.utils import Logger as log

## 초기화
# cw.init()
for i in range(100):
    log.debug(f'{i}, first')

