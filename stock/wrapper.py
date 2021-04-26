import os
import sys
import copy
import time
import pandas as pd

from django.db.models import Max, Min
from django_pandas.io import read_frame
from datetime import datetime, timedelta
from dateutil.parser import parse

from stock.models import Code, Company, MarketData, ModelingData, ModelingInfo, MyTrading, Account
from config.sysfiles.parameter import *
from trading.wrapper import BaseWrapper as bw
from trading.utils import Logger as log
from trading.utils import DataConverter as dc


class CodeWrapper:

    @staticmethod
    def get_type_list(c_type=SYSTEM_CODE_TYPE, is_name_index=False):
        """
        코드 타입별로 리스트를 구함
        :param c_type: 추출할 코드 타입(기본값은 시스템 코드)
        :param is_name_index:
          - True : 코드명을 인덱스로 생성, 값은 코드
          - False : 코드를 인덱스로 생성, 값은 코드명
        :return: 코드 타입의 리스트
        """
        try:
            data_qs = bw.gets(Code, 'code', c_type=c_type)
        except Exception as e:
            raise Exception(e)
        else:
            datas = {}
            for data in data_qs:
                if is_name_index:
                    datas[data.name] = data.code
                else:
                    datas[data.code] = data.name
            return datas


    @staticmethod
    def gets(*args, **kwargs):
        try:
            data_qs = bw.gets(Code, *args, **kwargs)
        except Exception as e:
            raise Exception(e)
        return data_qs


    @staticmethod
    def get(code, is_name=False):
        try:
            data = bw.get(Code, code=code)
            if is_name:
                data = data.name
        except Exception as e:
            raise Exception(e)
        return data


    @staticmethod
    def insert(datas):
        try:
            bw.insert(Code, datas)
        except Exception as e:
            raise Exception(e)


    @staticmethod
    def delete(**kwargs):
        try:
            bw.delete(Code, **kwargs)
        except Exception as e:
            raise Exception(e)


class CompanyWrapper:

    @staticmethod
    def make_object(data, update_data=None):
        company_dt = {}
        try:
            source = dc.other_to_dict(data)
            company_dt['com_code'] = source['com_code']
            company_dt['data_size'] = source.get('data_size', 0)

            if update_data is None:
                company_dt['id'] = None
            else:
                # 갱신용 데이터가 있는 경우에는 기존 ID를 저장하고,
                # 갱신용 데이터를 소스 데이터로 치환해 소스코드를 간략화 함.
                company_dt['id'] = source['id']
                source = dc.other_to_dict(update_data)

            company_dt['com_name']  = source['com_name']
            company_dt['m_type']    = source['m_type']
            company_dt['t_volume']  = source['t_volume']

            new_object = Company(**company_dt)
        except Exception as e:
            log.error(e)
            log.error(f'error data: data={data}, update_data={update_data}, '
                      f'company_df={company_dt}')
            new_object = None
        return new_object


    @staticmethod
    def gets(*args, **kwargs):
        try:
            data_qs = bw.gets(Company, *args, **kwargs)
        except Exception as e:
            raise Exception(e)
        return data_qs


    @staticmethod
    def gets_modeling_target():
        try:
            data_qs = bw.gets(Company,
                              'com_code',
                              data_size__gt=MODELING_SKIP_DATA_SIZE)
        except Exception as e:
            raise Exception(e)
        return data_qs


    @staticmethod
    def get(com_code):
        try:
            data = bw.get(Company, com_code=com_code)
        except Exception as e:
            raise Exception(e)
        return data


    @staticmethod
    def insert(datas):
        try:
            bw.insert(Company, datas)
        except Exception as e:
            raise Exception(e)


    @staticmethod
    def delete(**kwargs):
        try:
            bw.delete(Company, **kwargs)
        except Exception as e:
            raise Exception(e)


class MarketDataWrapper:

    @staticmethod
    def get_date(is_min=False, is_add_one=True):
        try:
            date = bw.get_date(MarketData, is_min=is_min, is_add_one=is_add_one)
        except Exception as e:
            raise Exception(e)
        return date


    @staticmethod
    def gets(*args, **kwargs):
        try:
            data_qs = bw.gets(MarketData, *args, **kwargs)
        except Exception as e:
            raise Exception(e)
        return data_qs


    @staticmethod
    def get(**kwargs):
        try:
            data = bw.get(MarketData, **kwargs)
        except Exception as e:
            raise Exception(e)
        return data


    @staticmethod
    def insert(datas):
        try:
            bw.insert(MarketData, datas)
        except Exception as e:
            raise Exception(e)


    @staticmethod
    def delete(**kwargs):
        try:
            bw.delete(MarketData, **kwargs)
        except Exception as e:
            raise Exception(e)


class ModelingDataWrapper:

    @staticmethod
    def get_date(is_min=False, is_add_one=False):
        try:
            date = bw.get_date(ModelingData, is_min=is_min, is_add_one=is_add_one)
        except Exception as e:
            raise Exception(e)
        return date


    @staticmethod
    def gets(*args, **kwargs):
        try:
            data_qs = bw.gets(ModelingData, *args, **kwargs)
        except Exception as e:
            raise Exception(e)
        return data_qs


    @staticmethod
    def get(**kwargs):
        try:
            data = bw.get(ModelingData, **kwargs)
        except Exception as e:
            raise Exception(e)
        return data


    @staticmethod
    def insert(datas):
        try:
            bw.insert(ModelingData, datas)
        except Exception as e:
            raise Exception(e)


    @staticmethod
    def delete(**kwargs):
        try:
            bw.delete(ModelingData, **kwargs)
        except Exception as e:
            raise Exception(e)


class ModelingInfoWrapper:

    @staticmethod
    def gets(*args, **kwargs):
        try:
            data_qs = bw.gets(ModelingInfo, *args, **kwargs)
        except Exception as e:
            raise Exception(e)
        return data_qs


    @staticmethod
    def get(**kwargs):
        try:
            data = bw.get(ModelingInfo, **kwargs)
        except Exception as e:
            raise Exception(e)
        return data


    @staticmethod
    def insert(datas):
        try:
            bw.insert(ModelingInfo, datas)
        except Exception as e:
            raise Exception(e)


    @staticmethod
    def delete(**kwargs):
        try:
            bw.delete(ModelingInfo, **kwargs)
        except Exception as e:
            raise Exception(e)


class AccountWrapper:

    @staticmethod
    def gets(*args, **kwargs):
        try:
            data_qs = bw.gets(Account, *args, **kwargs)
        except Exception as e:
            raise Exception(e)
        return data_qs


    @staticmethod
    def get(**kwargs):
        try:
            data = bw.get(Account, **kwargs)
        except Exception as e:
            raise Exception(e)
        return data


    @staticmethod
    def insert(datas):
        try:
            bw.insert(Account, datas)
        except Exception as e:
            raise Exception(e)


    @staticmethod
    def delete(**kwargs):
        try:
            bw.delete(Account, **kwargs)
        except Exception as e:
            raise Exception(e)
