import os
import sys

project_path = os.path.abspath(__file__+'/../../..')
if project_path not in sys.path:
    sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

import re_test
import shutil
import pandas as pd
import copy

from tqdm import tqdm
from django_pandas.io import read_frame

from config.sysfiles.parameter import *
from trading.utils import Logger as log
from trading.utils import DataConverter as dc
from trading.utils import StartEndLogging
from trading.crawler import KrxCrawler
from stock.wrapper import CodeWrapper as scdw
from stock.wrapper import CompanyWrapper as scw
from stock.wrapper import MarketDataWrapper as smdw
from stock.wrapper import ModelingDataWrapper as smlw

MERGE_FILE_PATH = os.path.join(os.path.expanduser('~'), 'projects',
                               'Data', 'crawling', 'krx', 'merge', 'merge.csv')

def insert_marketdata_from_mergefile():
    insert_se = StartEndLogging('insert marketdata')

    col_names = ['com_code', 'com_name', 'm_type', 'm_dept', 'close',
                 'diff', 'ratio', 'open', 'high', 'low', 'volume',
                 'value', 't_value', 't_volume', 'date']
    # merge_reader = pd.read_csv(MERGE_FILE_PATH, encoding='CP949', low_memory=False,
    #                            names=col_names, chunksize=3000, skiprows=[0])
    #
    # loop_cnt = 1
    # for merge_df in merge_reader:
    #     merge_df = merge_df.fillna(0)
    #     smdw.insert(merge_df)
    #     insert_se.mid(f'{loop_cnt * 3000}')
    #     loop_cnt += 1

    smdw.delete()

    insert_se.end()


if __name__ == '__main__':
    insert_marketdata_from_mergefile()