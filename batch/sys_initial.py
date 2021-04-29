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
from stock.wrapper import AccountWrapper as saw
from stock.wrapper import CompanyWrapper as scw
from stock.wrapper import MarketDataWrapper as smdw
from stock.wrapper import ModelingDataWrapper as smlw


def code_init():
    se = StartEndLogging()
    try:
        scdw.delete()
        code_df = pd.read_csv(CODE_FILE_PATH, delimiter=',', encoding='utf-8')
        code_df = code_df.fillna('')
        scdw.insert(code_df)
    except Exception as e:
        log.error(e)
        sys.exit()
    se.end(f'{len(code_df)} codes insert!')


def account_init():
    t_type_qs = scdw.get_type_list(c_type='B')
    account_list = []
    for t_type in t_type_qs:
        for cnt in TRADING_COUNT:
            account = {
                'acc_name'      : f'{t_type}{cnt}',
                't_type'        : t_type,
                't_count'       : cnt,
                'base_money'    : TRADING_BASE_MONEY
            }
            account_list.append(account)
    saw.delete()
    saw.insert(account_list)


def start_krx_crawling():
    kc = KrxCrawler()
    kc.start_crawler()


def insert_marketdata_from_crawler():

    m_type_dict = scdw.get_type_dict('A', is_name_index=True)

    def file_processing(csv_file_name):
        trading_df = pd.read_csv(os.path.join(CRAWLING_TARGET_PATH, csv_file_name),
                                 delimiter=',', encoding='CP949', names=COLUMN_NAMES,
                                 skiprows=[0])

        trading_df = trading_df.fillna(0)
        trading_df['date'] = parse(str(re.findall('\d{8}', csv_file_name)[0])).date()
        trading_df['m_type'] = trading_df['m_type']\
            .apply(lambda m_type: m_type_dict[str(m_type)])
        trading_df = trading_df.drop(['m_dept'], axis=1)

        smdw.insert(trading_df)

        shutil.move(os.path.join(CRAWLING_TARGET_PATH, csv_file_name),
                    os.path.join(CRAWLING_BACKUP_PATH, csv_file_name))

    se = StartEndLogging()
    try:
        for file_name in tqdm(sorted(os.listdir(CRAWLING_TARGET_PATH))):
            file_processing(file_name)
            se.mid(file_name)
    except Exception as e:
        log.error(e)
        sys.exit()
    se.end()


def insert_company_from_market():
    se = StartEndLogging()

    scw.delete()
    market_qs = smdw.gets(date=smdw.get_date(is_add_one=False))
    log.debug(f'market data size: {len(market_qs)}')

    company_objects = []
    for market_data in market_qs:
        company_object = scw.make_object(market_data)
        if company_object is not None:
            company_objects.append(company_object)
    scw.insert(company_objects)

    se.end()


def insert_modelingdata_from_market():
    se = StartEndLogging()

    company_qs = scw.gets('id')
    company_size = len(company_qs)
    log.debug(f'company size: {company_size}')
    smlw.delete()

    def get_normal_marketdata(com_code):
        company_market_qs = smdw.gets(com_code=com_code)
        first_data = company_market_qs.first()
        yesterday_data, first_normal_data = first_data, first_data
        if first_data.t_volume != 0:
            diff_ratio = company_market_qs.last().t_volume / first_data.t_volume
        else:
            # 첫번째 t_volume값이 0이기 때문에 전체 변동량 체크가 불가능함.
            # 따라서 세부 체크가 수행될 수 있도록 diff_ratio를 설정함
            diff_ratio = TOTAL_CHECK_MAX_RATIO + 1.

        if diff_ratio > TOTAL_CHECK_MAX_RATIO or diff_ratio < TOTAL_CHECK_MIN_RATIO:
            for market_data in company_market_qs[1:]:   # 첫번째 값은 위에서 first()을 이용해 이미 사용
                if yesterday_data.t_volume != 0 and market_data.t_volume != 0:
                    diff_ratio = market_data.t_volume / yesterday_data.t_volume
                    if diff_ratio > DAY_CHECK_MAX_RATIO or diff_ratio < DAY_CHECK_MIN_RATIO:
                        first_normal_data = market_data
                    # 당일 거래량이 없는 종목은 감자/증자 대상으로 간주한다.
                    if market_data.volume == 0:
                        first_normal_data = market_data
                yesterday_data = market_data

        normal_qs = company_market_qs.filter(date__gte=first_normal_data.date)
        log.debug(f'com_code: {com_code},  modeling data size: '
                  f'total({len(company_market_qs)}), normal({len(normal_qs)})')
        return normal_qs

    for company in tqdm(company_qs):
        market_df = read_frame(get_normal_marketdata(company.com_code))
        company.data_size = len(market_df)
        company.save()
        market_df = market_df[['date', 'com_code']+MODELING_COLUMNS]
        smlw.insert(market_df)

    se.end()


if __name__ == '__main__':
    code_init()
    account_init()
    # start_krx_crawling()
    # insert_marketdata_from_crawler()
    # insert_company_from_market()
    # insert_modelingdata_from_market()