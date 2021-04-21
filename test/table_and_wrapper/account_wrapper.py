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
from stock.models import Account
from stock.wrapper import AccountWrapper as saw


def insert_and_update():
    account_dt = {
        'id'        : None,
        'acc_name'  : 'ccccc',
        't_type'    : 'aaaa',
        't_count'   : 3,
        'base_money': 2000000,
    }
    saw.insert(account_dt)


def get_and_update():
    data_qs = saw.get_datas()
    # 1개, dict, Account
    # n개, QuerySet, list, DataFrame
    log.info(f'get account name: {data_qs[0].acc_name}')
    log.debug(f'get account data: {data_qs}')

    data_qs.base_money = 3000000
    saw.insert(data_qs)


if __name__ == '__main__':
    # insert_and_update()
    get_and_update()