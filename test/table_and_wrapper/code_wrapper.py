import os
import sys
import pandas as pd

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
        cdw.delete()
        code_df = pd.read_csv(CODE_FILE_PATH, delimiter=',', encoding='utf-8')
        code_df = code_df.fillna('')
        cdw.insert(code_df)
    except Exception as e:
        log.error(e)
        sys.exit()
    se.end(f'{len(code_df)} codes insert!')

def insert():
    code_dt = {
        'c_type': 'B',
        'code': 'B003',
        'name': 'Next Close vs Next Open',
        'memo': 'Next day predict close price vs next day predict open price'
    }
    cdw.insert(code_dt)

def insert_err():
    code_dt = {
        'err': 'error',
        'c_type': 'B',
        'code': 'B003',
        'name': 'Next Close vs Next Open',
        'memo': 'Next day predict close price vs next day predict open price'
    }
    try:
        cdw.insert(code_dt)
    except Exception as e:
        log.error(e)
        sys.exit()

def update():
    code = cdw.get(code='B002')
    code.name = 'Next Close vs Today Close'
    code.memo = 'Next day predict close price vs today real close price'
    cdw.insert(code)

def get():
    code = cdw.get(code='B002')
    log.debug(code)
    code = cdw.get(code='B002', is_name=True)
    log.debug(code)

def gets(*args, **kwargs):
    try:
        code_qs = cdw.gets(*args, **kwargs)
        for code in code_qs:
            log.debug(code)
    except Exception as e:
        log.error(e)
        sys.exit()

if __name__ == '__main__':
    code_init()
    # insert()
    # update()
    # insert_err()
    # gets()
    # gets(c_type='A')
    # gets('-code', c_type='A')
    # gets('-id')
    # get()