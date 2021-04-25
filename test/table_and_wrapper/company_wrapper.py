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
from stock.wrapper import CompanyWrapper as scw

def save_from_marketdata():
    market_qs = scw.save_from_marketdata()
    log.debug(f'market_qs size: {len(market_qs)}')

def get_data():
    company = scw.get('060310')
    log.debug(company)
    company_qs = scw.gets('id')
    for com in company_qs[:2]:
        log.debug(com)


if __name__ == '__main__':
    # save_from_marketdata()
    get_data()