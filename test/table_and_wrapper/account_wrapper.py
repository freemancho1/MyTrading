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
from trading.utils import DataConverter as dc
from stock.models import Account
from stock.wrapper import AccountWrapper as saw


def insert_and_update():

    adt1 = {
        'acc_name'  : 'ccccc',
        't_type'    : 'aaaa',
        't_count'   : 3,
        'base_money': 2000000
    }
    adt2 = {
        'acc_name'  : 'ddddd',
        't_type'    : 'aaaa',
        't_count'   : 4,
        'base_money': 3000000
    }
    adt3 = {
        'id'        : [5],
        'acc_name'  : ['ccccc'],
        't_type'    : ['aaaa'],
        't_count'   : ['5'],
        'base_money': [4000000]
    }

    # saw.insert(adt1)
    # log.debug('\n\n')
    # saw.insert(pd.Series(adt2))
    # log.debug('\n\n')
    # saw.insert(pd.DataFrame.from_dict(adt3))
    # log.debug('\n\n')

    # acc1 = saw.get_datas(acc_name='bbbbb')
    # acc1.base_money = 4000000
    # saw.insert(acc1)
    # log.debug('\n\n')

    # QuerySet은 직접 수정이 안되기 때문에 insert에서 제외
    # acc2 = saw.get_datas(t_type='aaaa')
    # acc2[0].balance = 10 # 직접 수정 안됨
    # saw.insert(acc2)
    # log.debug('\n\n')

    # acc3 = saw.get_datas(t_type='aaaa')
    # acc_list = []
    # for acc in acc3:
    #     acc.balance = 20.
    #     acc_list.append(acc)
    # saw.insert(acc_list)
    # log.debug('\n\n')

    # acc4 = saw.get_datas(t_type='aaaa')
    # acc_list1 = []
    # for acc in acc4:
    #     acc.balance = 10.
    #     tmp_acc = dc.other_to_dict(acc)
    #     log.info(tmp_acc)
    #     acc_list1.append(tmp_acc)
    # saw.insert(acc_list1)
    # log.debug('\n\n')

    acc3 = saw.get_datas(t_type='aaaa')
    acc_df = read_frame(acc3)
    saw.insert(acc_df)
    log.debug('\n\n')

def get_and_update():
    data_qs = saw.get_datas()
    # 1개, dict, Account
    # n개, QuerySet, list, DataFrame
    log.info(f'get account name: {data_qs[0].acc_name}')
    log.debug(f'get account data: {data_qs}')

    data_qs.base_money = 3000000
    saw.insert(data_qs)


if __name__ == '__main__':
    insert_and_update()
    # get_and_update()