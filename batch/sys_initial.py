import os
import sys

project_path = os.path.abspath(__file__+'/../..')
if project_path not in sys.path:
    sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

import re
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


def code_init():
    scdw.init()

def start_krx_crawling():
    kc = KrxCrawler()
    kc.start_crawler()

def insert_marketdata_from_crawler():

    def file_processing(csv_file_name):
        trading_df = pd.read_csv(os.path.join(CRAWLING_TARGET_PATH, csv_file_name),
                                 delimiter=',', encoding='CP949', names=COLUMN_NAMES,
                                 skiprows=[0])
        trading_df = trading_df.fillna(0)
        trading_df['date'] = re.findall('\d{8}', csv_file_name)[0]

        smdw.insert(trading_df)

        shutil.move(os.path.join(CRAWLING_TARGET_PATH, csv_file_name),
                    os.path.join(CRAWLING_BACKUP_PATH, csv_file_name))

    se = StartEndLogging()
    try:
        for file_name in tqdm(sorted(os.listdir(CRAWLING_TARGET_PATH))):
            file_processing(file_name)
    except Exception as e:
        log.error(e)
        sys.exit()
    se.end()


def insert_company_from_market():
    se = StartEndLogging()

    scw.delete_all()
    market_qs = smdw.get_datas(date=smdw.get_date(is_add_one=False))
    log.debug(f'market data size: {len(market_qs)}')

    company_objects = []
    for market_data in market_qs:
        company_objects.append(scw.make_object(market_data))
    scw.insert(company_objects)

    se.end()


def insert_modelingdata_from_market():
    se = StartEndLogging()

    company_qs = scw.get_datas()
    company_size = len(company_qs)
    log.debug(f'company size: {company_size}')
    smlw.delete_all()

    def get_normal_marketdata(com_code):
        company_market_qs = smdw.get_datas(com_code=com_code)
        first_data = company_market_qs.first()
        yesterday_data, first_normal_data = first_data, first_data
        diff_ratio = 0.
        if first_data.t_volume != 0:
            diff_ratio = company_market_qs.last().t_volume / first_data.t_volume

        if diff_ratio > TOTAL_CHECK_MAX_RATIO or diff_ratio < TOTAL_CHECK_MIN_RATIO:
            for market_data in company_market_qs[1:]:   # 첫번째 값은 위에서 first()을 이용해 이미 사용
                if yesterday_data.t_volume != 0 and market_data.t_volume != 0:
                    diff_ratio = market_data.t_volume / yesterday_data.t_volume
                    if diff_ratio > DAY_CHECK_MAX_RATIO or diff_ratio < DAY_CHECK_MIN_RATIO:
                        first_normal_data = market_data
                yesterday_data = market_data

        normal_qs = company_market_qs.filter(date__gte=first_normal_data.date)
        log.debug(f'{com_code} modeling data size: '
                  f'total({len(company_market_qs)}), normal({len(normal_qs)})')
        return normal_qs

    for company in company_qs[:1]:
        market_df = read_frame(get_normal_marketdata(company.com_code))
        company.data_size = len(market_df)
        company.save()
        log.info(company)
        smlw.insert(smlw.make_objects(market_df, company))

    modeling_qs = smlw.get_datas(date='2009-01-21')
    log.warning(f'modeling_qs: {modeling_qs}')
    # for modeling_data in modeling_qs[:1]:
    #     log.warning(modeling_data.company_id)

    se.end()


if __name__ == '__main__':
    # code_init()
    # start_krx_crawling()
    # insert_marketdata_from_crawler()
    # insert_company_from_market()
    insert_modelingdata_from_market()