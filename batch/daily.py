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
from stock.wrapper import AccountWrapper as saw
from stock.wrapper import CompanyWrapper as scw
from stock.wrapper import MarketDataWrapper as smdw
from stock.wrapper import ModelingDataWrapper as smlw
from stock.wrapper import ModelingInfoWrapper as smiw
from stock.wrapper import MyTradingWrapper as smyw
from modeling.nn_training import LstmTraining


def start_krx_crawling():
    kc = KrxCrawler()
    kc.start_crawler()

def update_marketdata_from_crawler():

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


def today_modeling():
    se = StartEndLogging()

    modeling_target_qs = scw.gets_modeling_target()
    modeling_size = len(modeling_target_qs)

    cnt_processing = 0
    cnt_skip_trend, cnt_skip_accuracy = 0, 0
    for modeling_company in modeling_target_qs:
        model = LstmTraining(modeling_company.com_code, LSTM_KWARGS)
        is_skip = model.modeling2()
        cnt_processing += 1
        se.mid(f'{modeling_company.com_code}, {cnt_processing}/{modeling_size}')
        if is_skip['trend']:
            cnt_skip_trend += 1
        if is_skip['accuracy']:
            cnt_skip_accuracy += 1
    log.info(f'modeling total count: {len(modeling_target_qs)}, '
             f'trend skip: {cnt_skip_trend}, accuracy skip: {cnt_skip_accuracy}')

    se.end()


def today_trading():

    def save_trading(t_type, data_qs):
        try:
            idx = 0
            for data in data_qs[:TRADING_MAX_COUNT]:
                trading_dt = {
                    'date': data.date,
                    'com_code': data.com_code,
                    't_type': t_type,
                    'p_close': data.p_close,
                }
                if idx < TRADING_MIN_COUNT:
                    trading_dt['t_count'] = TRADING_MIN_COUNT
                    smyw.insert(trading_dt)
                if idx < TRADING_MID_COUNT:
                    trading_dt['t_count'] = TRADING_MID_COUNT
                    smyw.insert(trading_dt)
                if idx < TRADING_MAX_COUNT:
                    trading_dt['t_count'] = TRADING_MAX_COUNT
                    smyw.insert(trading_dt)
                idx += 1
        except Exception as e:
            raise Exception(e)

    try:
        target_date = smiw.get_date()
        save_trading('B001', smiw.gets_target_accuracy(target_date))
        save_trading('B002', smiw.gets_target_price(target_date))
    except Exception as er:
        raise Exception(er)


def yesterday_trading_result():

    try:
        t_type_qs = scdw.get_type_list(c_type='B')
        y_date = smyw.get_date()
        for t_type in t_type_qs:
            for cnt in TRADING_COUNT:
                y_trading_qs = smyw.gets_yesterday_data(y_date, t_type, cnt)
                account = saw.get_trading_account(t_type, cnt)
                base_money = account.base_money
                base_money_for_cnt = int(base_money / cnt)
                total_money = 0
                for y_trading in y_trading_qs:
                    modeling_data = smlw.gets_trading_data(y_date, y_trading.com_code)
                    y_trading.buy_price = modeling_data.open
                    y_trading.sell_price = modeling_data.close
                    y_trading.ratio = modeling_data.close / modeling_data.open
                    y_trading.volume = int(base_money_for_cnt / modeling_data.open)
                    y_trading.profit = (y_trading.sell_price - y_trading.buy_price) \
                                       * y_trading.volume

                    buy_money = y_trading.buy_price * y_trading.volume
                    diff_money = base_money_for_cnt - buy_money
                    sell_money = y_trading.sell_price * y_trading.volume
                    result_money = diff_money + sell_money
                    total_money += result_money

                    y_trading.save()

                account.balance = total_money - TRADING_BASE_MONEY
                account.ratio = total_money / TRADING_BASE_MONEY
                account.base_money = total_money
                account.save()
    except Exception as e:
        raise Exception(e)


if __name__ == '__main__':
    tse = StartEndLogging('daily processing')

    try:
        start_krx_crawling()
        update_marketdata_from_crawler()
        update_company_from_market()
        update_modelingdata_from_market()
        yesterday_trading_result()
        # today_modeling()
        # today_trading()
    except Exception as err:
        log.error(err)

    tse.end('daily processing')