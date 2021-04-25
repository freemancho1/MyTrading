import os
import sys
import pandas as pd

project_path = os.path.abspath(__file__+'/../../..')
if project_path not in sys.path:
    sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django_pandas.io import read_frame

from config.sysfiles.parameter import *
from trading.utils import Logger as log
from stock.wrapper import BaseWrapper as sbw
from stock.models import Code


def get_test():
    try:
        code = sbw.get(Code, c_type='A', code='A005')
        log.debug(code)
    except Exception as e:
        log.error(e)

def get_datas_test():
    try:
        code_qs = sbw.gets(Code, '-code', id=100)
    except Exception as e:
        log.error(e)
    else:
        for code in code_qs:
            log.debug(code)

def delete_test():
    sbw.delete(Code)
    get_datas_test()


def insert_test():
    sbw.delete(Code)
    code_df = pd.read_csv(CODE_FILE_PATH, delimiter=',', encoding='utf-8')
    code_df = code_df.fillna('')
    sbw.insert(Code, code_df)


if __name__ == '__main__':
    get_test()
    # get_datas_test()
    # delete_test()
    # insert_test()