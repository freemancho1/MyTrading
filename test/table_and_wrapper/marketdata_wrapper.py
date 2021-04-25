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
from stock.wrapper import MarketDataWrapper as smdw


def get_date():
    log.debug(f'max date: {smdw.get_date()}')
    log.debug(f'max data + 1days: {smdw.get_date(is_add_one=True)}')
    log.debug(f'min date: {smdw.get_date(is_min=True)}')

def insert():
    trading_df = pd.read_csv(os.path.join(CRAWLING_TARGET_PATH, '20210414.csv'),
                             delimiter=',', encoding='CP949', names=COLUMN_NAMES,
                             skiprows=[0])

    trading_df = trading_df.fillna(0)
    trading_df['date'] = parse(str(re.findall('\d{8}', csv_file_name)[0])).date()
    trading_df['m_type'] = trading_df['m_type'] \
        .apply(lambda m_type: m_type_list[str(m_type)])
    trading_df = trading_df.drop(['m_dept'], axis=1)

    smdw.insert(trading_df)

def delete():
    smdw.delete()

if __name__ == '__main__':
    # get_date()
    # get_datas()
    insert()
    # delete()