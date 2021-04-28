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
from stock.wrapper import ModelingInfoWrapper as smiw
from stock.wrapper import MyTradingWrapper as smyw


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


if __name__ == '__main__':
    try:
        today_trading()
    except Exception as err:
        log.error(err)