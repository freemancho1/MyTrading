import os
import re
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
from trading.utils import Logger as log
from trading.utils import DataConverter as dc


class CodeWrapper:

    @staticmethod
    def init():
        Code.objects.all().delete()

        codes_df = pd.read_csv(CODE_FILE_PATH, delimiter=',', encoding='utf-8')
        codes_df = codes_df.fillna('')

        for _, code in codes_df.iterrows():
            try:
                code['id'] = None
                code_object = Code(**code)
                code_object.save()
            except Exception as e:
                log.error(e)


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
        codes_qs = Code.objects.filter(c_type=c_type)
        codes = {}
        for code in codes_qs:
            if is_name_index:
                codes[code.name] = code.code
            else:
                codes[code.code] = code.name
        return codes


    @staticmethod
    def get_code(code):
        try:
            _code = Code.objects.get(code=code)
        except Exception as e:
            log.error(e)
            _code = None
        return _code



    @staticmethod
    def get_name(code):
        try:
            name = Code.objects.get(code=code).name
        except Exception as e:
            log.error(e)
            name = None
        return name


class CompanyWrapper:

    @staticmethod
    def get_datas(com_code=None):
        """
        회사코드를 이용해 특정 회사 정보를 추출하거나,
        전체 데이터를 추출한다.(com_code is None)
        :param com_code: 추출할 회사코드 또는 None(전체 추출)
        :return: 특정 또는 전체 회사정보
        """
        if com_code is None:
            company_qs = Company.objects.all().order_by('id')
            return company_qs
        else:
            try:
                # objects.get() 함수는 원하는 값이 없는 경우 에러가 발생함
                company = Company.objects.get(com_code=com_code)
            except Exception as e:
                log.error(e)
                company = None
            return company


    @staticmethod
    def make_object(data, update_data=None):
        company_dt = {}
        try:
            source = dc.other_to_dict(data)
            company_dt['com_code'] = source['com_code']
            company_dt['data_size'] = source.get('data_size', 0)

            if update_data is not None:
                # 갱신용 데이터가 있는 경우에는 기존 ID를 저장하고,
                # 갱신용 데이터를 소스 데이터로 치환해 소스코드를 간략화 함.
                company_dt['id'] = source['id']
                source = dc.other_to_dict(update_data)
            else:
                company_dt['id'] = None

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
    def insert(datas):
        data_type = str(type(datas))
        if 'dict' in data_type:
            pass
        elif 'list' in data_type:
            for data in datas:
                data.save()
        elif 'DataFrame' in data_type:
            pass
        else:
            log.error(f'Unsupported type - {data_type}')
            sys.exit()


    @staticmethod
    def delete_all():
        Company.objects.all().delete()


class MarketDataWrapper:

    @staticmethod
    def get_date(is_min=False, is_add_one=True):
        """
        MarketData의 최대/최소 일자를 구한다.
        :param is_min: Treu - 최소일자, False - 최대일자
        :param is_add_one: 최대일자에(만) 참이면 1일을 더한다.
        :return: 최소/최대(또는 +1일) 일자, 단, Table에 값이 없으면 최초 거래일
        """
        if is_min:
            date = MarketData.objects.all().aggregate(min_date=Min('date'))['min_date']
        else:
            date = MarketData.objects.all().aggregate(max_date=Max('date'))['max_date']

        if date is not None:
            if is_add_one and not is_min:
                date = date + timedelta(days=1)
        else:
            date = parse(BASE_TRADING_DATE)

        return date


    @staticmethod
    def get_datas(com_code=None, date=None, period=None):
        """
        주어진 조건을 이용해 MarketData를 가져온다.
        :param com_code: 회사코드
        :param date: 일자정보
        :param period: 기간정보(None이면 전체 기간)
        :return: 조건에 맞는 MarketData (데이터가 없으면 <QuerySet []> 리턴)
        """
        if com_code is None and date is None and period is None:
            data_qs = MarketData.objects.all()
        else:
            data_qs = MarketData.objects
            if com_code:
                data_qs = data_qs.filter(com_code=com_code)
            if date:
                data_qs = data_qs.filter(date=date)
            elif period:
                data_qs = data_qs.filter(date__gte=period['start'], date__lte=period['end'])
        data_qs = data_qs.order_by('date')
        return data_qs


    @staticmethod
    def insert(data_df):

        # CODE type 'A': Market Type(KOSDAC, KOSPI..)
        m_type_list = CodeWrapper.get_type_list('A', is_name_index=True)

        def make_object(data):
            """
            <class 'pandas.core.series.Series'> 형태의 입력값을 받아
            MarketData 클래스로 리턴한다.
            :param data: 시리즈 형태의 MarketData 데이터
              - 이 테이블은 항상 신규로 데이터를 저장만 하기 때문에 id=None으로 하고,
              - 문자열로 되어 있는 날짜정보 날짜 형식으로 변환하고,
              - m_type은 변환하고,
              - 필요없는 m_dept는 드랍한 후 저장한다.
            :return: MarketData object
            """
            try:
                data['id'] = None
                data['date'] = parse(str(data['date'])).date()
                data['m_type'] = m_type_list[str(data['m_type'])]
                data = data.drop('m_dept')
            except Exception as e:
                log.error(e)
                return None
            return MarketData(**data)

        objects = []
        for _, market_data in data_df.iterrows():
            new_object = make_object(market_data)
            if new_object is not None:
                objects.append(new_object)

        MarketData.objects.bulk_create(objects)


    @staticmethod
    def delete_all():
        MarketData.objects.all().delete()


class ModelingDataWrapper:

    @staticmethod
    def get_datas(company_id=None, date=None, period=None):
        if company_id is None and date is None and period is None:
            data_qs = ModelingData.objects.all()
        else:
            data_qs = ModelingData.objects
            if company_id:
                data_qs = data_qs.filter(company_id=company_id)
            if date:
                data_qs = data_qs.filter(date=date)
            elif period:
                data_qs = data_qs.filter(date__gte=period['start'], date__lte=period['end'])
        data_qs = data_qs.order_by('date')
        return data_qs


    @staticmethod
    def insert(datas):

        def make_object(data_df):
            market_df = copy.deepcopy(data_df[['date', 'com_code']+MODELING_COLUMNS])
            market_df['id'] = None
            return market_df

        modeling_objects = []
        for _, data in make_object(datas).iterrows():
            try:
                new_object = ModelingData(**data)
                modeling_objects.append(new_object)
            except:
                log.error(data)
        ModelingData.objects.bulk_create(modeling_objects)


    @staticmethod
    def delete_all():
        ModelingData.objects.all().delete()


class AccountWrapper:

    @staticmethod
    def insert(datas):
        base_table = Account

        def make_object(new_data):
            if 'DataFrame' in str(type(new_data)):
                new_data = dc.other_to_dict(new_data)
            new_data['id'] = new_data.get('id', None)
            return base_table(**new_data)

        def save_list(lists):
            for data in lists:
                data.save()

        def insert_list(lists):
            subs_type = re.findall(".*\.(\w+)\.",
                                   str(type(lists[0])).replace("'", "."))[0]
            if subs_type in str(base_table):
                if lists[0].id is not None:
                    save_list(lists)
                else:
                    base_table.objects.bulk_create(datas)
            elif subs_type in ['dict', 'Series']:
                new_objects = []
                for data in lists:
                    new_objects.append(make_object(data))
                if datas[0]['id'] is not None:
                    save_list(new_objects)
                else:
                    base_table.objects.bulk_create(new_objects)
            else:
                log.error(f'Unsupported type : {datas_type} - {subs_type}')

        def insert_df(dataframes):
            new_objects = []
            for _, data in dataframes.iterrows():
                new_objects.append(make_object(data))
            if new_objects[0].id is not None:
                save_list(new_objects)
            else:
                base_table.objects.bulk_create(new_objects)

        datas_type = re.findall(".*\.(\w+)\.",
                                str(type(datas)).replace("'","."))[0]
        # datas의 type이 'base_table'값이면 len()함수가 오류가 나기 때문에 1로 지정
        datas_size = 1 if datas_type in str(base_table) else len(datas)
        log.debug(f'datas size: {datas_size}, datas type: {datas_type}')

        if datas_type in str(base_table):
            datas.save()
        elif (datas_type == 'DataFrame' and datas_size == 1) or \
             datas_type in ['dict', 'Series']:
            make_object(datas).save()
        elif datas_type == 'list':
            insert_list(datas)
        elif datas_type == 'DataFrame':
            insert_df(datas)
        else:
            log.error(f'Unsupported type : {datas_type}')


    @staticmethod
    def get_datas(acc_name=None, t_type=None):
        if acc_name is not None:
            # unique field
            data_qs = Account.objects.get(acc_name=acc_name)
        elif t_type is not None:
            data_qs = Account.objects.filter(t_type=t_type).order_by('acc_name')
        else:
            data_qs = Account.objects.all().order_by('acc_name')
        return data_qs


    @staticmethod
    def delete_all():
        Account.objects.all().delete()