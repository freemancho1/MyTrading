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

from tqdm import tqdm
from dateutil.parser import parse
from django_pandas.io import read_frame

from config.sysfiles.parameter import *
from trading.utils import Logger as log
from trading.utils import StartEndLogging
from trading.crawler import KrxCrawler
from stock.wrapper import CodeWrapper as scdw
from stock.wrapper import CompanyWrapper as scw
from stock.wrapper import MarketDataWrapper as smdw
from stock.wrapper import ModelingDataWrapper as smlw


def start_krx_crawling():
    kc = KrxCrawler()
    kc.start_crawler()

def update_marketdata_from_crawler():

    m_type_list = scdw.get_type_list('A', is_name_index=True)

    def file_processing(csv_file_name):
        trading_df = pd.read_csv(os.path.join(CRAWLING_TARGET_PATH, csv_file_name),
                                 delimiter=',', encoding='CP949', names=COLUMN_NAMES,
                                 skiprows=[0])

        trading_df = trading_df.fillna(0)
        trading_df['date'] = parse(str(re.findall('\d{8}', csv_file_name)[0])).date()
        trading_df['m_type'] = trading_df['m_type']\
            .apply(lambda m_type: m_type_list[str(m_type)])
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


def update_company_from_market():
    se = StartEndLogging()

    market_qs = smdw.gets(date=smdw.get_date(is_min=False, is_add_one=False))
    company_df = read_frame(scw.gets('id'))
    log.debug(f'market data size: {len(market_qs)}, company data size: {len(company_df)}')

    company_objects = []
    for market_data in market_qs:
        company = company_df[company_df['com_code']==market_data.com_code]
        if company.empty:
            company_object = scw.make_object(market_data)
        else:
            company_object = scw.make_object(company, market_data)
        if company_object is not None:
            company_objects.append(company_object)

    scw.insert(company_objects)

    se.end()


def update_modelingdata_from_market():
    """
    daily 작업에서는 추가되는 회사 데이터의 건수에 대한 카운팅은 무시하고
    업데이트 되지 않은 마켓 데이터를 일괄로 추가한다.
    - 이 작업은 시스템 초기화나 주간 작업에서만 수행한다.
    :return: 없음
    """
    se = StartEndLogging()

    try:
        data_df = read_frame(smdw.gets('date', date__gt=smlw.get_date()))
        smlw.insert(data_df[['date','com_code']+MODELING_COLUMNS])
    except Exception as e:
        log.error(e)
        sys.exit()

    se.end()


if __name__ == '__main__':
    tse = StartEndLogging('daily processing')

    start_krx_crawling()
    update_marketdata_from_crawler()
    update_company_from_market()
    update_modelingdata_from_market()

    tse.end('daily processing')