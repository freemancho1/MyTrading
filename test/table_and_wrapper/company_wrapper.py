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
from stock.models import Company
from stock.wrapper import CompanyWrapper as cw

def save_from_marketdata():
    market_qs = cw.save_from_marketdata()
    log.debug(f'market_qs size: {len(market_qs)}')


if __name__ == '__main__':
    save_from_marketdata()