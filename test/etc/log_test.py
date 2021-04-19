import os
import sys

project_path = os.path.abspath(__file__+'/../../..')
if project_path not in sys.path:
    sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from config.sysfiles.parameter import *
from trading.utils import Logger as log
import time


log.debug(f'*****************************')
log.info(f'*****************************')
log.warning(f'*****************************')
log.error(f'*****************************')
log.critical(f'*****************************')
