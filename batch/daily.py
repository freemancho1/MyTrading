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
from django_pandas.io import read_frame

from config.sysfiles.parameter import *
from trading.utils import Logger as log
from trading.utils import StartEndLogging
from stock.wrapper import CompanyWrapper as scw
from stock.wrapper import MarketDataWrapper as smdw


def insert_krx_crawling_data():

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

    market_qs = smdw.get_datas(date=smdw.get_date(is_min=False, is_add_one=False))
    company_df = read_frame(scw.get_datas())
    log.debug(f'market data size: {len(market_qs)}, company data size: {len(company_df)}')

    company_objects = []
    for market_data in market_qs:
        company = company_df[company_df['com_code']==market_data.com_code]
        if company.empty:
            company_object = scw.make_object(market_data)
        else:
            company_object = scw.make_object(company, market_data)
        company_objects.append(company_object)

    scw.insert(company_objects)

    se.end()


if __name__ == '__main__':
    # insert_krx_crawling_data()
    insert_company_from_market()