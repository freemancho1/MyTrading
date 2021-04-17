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


def save_company():
    company = {
        'id': 1,
        'com_code': '1aaaaaa',
        'com_name': '1bbbbbbb',
        'm_type': 'ccc',
        't_volume': 1.,
        'data_size': 11
    }
    log.info(company)
    Company(**company).save()


if __name__ == '__main__':
    save_company()
