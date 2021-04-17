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
from trading.utils import StartEndLogging
from stock.wrapper import CodeWrapper as cdw


def code_init():
    se = StartEndLogging()
    try:
        cdw.init()
    except Exception as e:
        log.error(e)
    se.end()

def get_type():
    log.debug(f'codes: {cdw.get_type("A")}')

if __name__ == '__main__':
    # code_init()
    get_type()