from datetime import datetime
from django.db import models
import numpy as np


class Code(models.Model):

    c_type      = models.CharField('Code Type', max_length=1, null=False)
    code        = models.CharField('Code', max_length=4, null=False, db_index=True)
    name        = models.CharField('Code Name', max_length=100, null=False)
    memo        = models.CharField('Memo', max_length=999)

    class Meta:
        ordering = ['c_type', 'code']

    def __init__(self, id, c_type, code, name, memo=None,
                 *args, **kwargs):
        super(Code, self).__init__(*args, **kwargs)
        self.id     = id
        self.c_type = c_type
        self.code   = code
        self.name   = name
        self.memo   = memo

    def __str__(self):
        return f'Code(id={self.id}, c_type={self.c_type}, code={self.code}, ' \
               f'name={self.name}, memo={self.memo})'


class Company(models.Model):

    com_code    = models.CharField('Company Code', max_length=7, null=False, db_index=True)
    com_name    = models.CharField('Company Name', max_length=500, null=False)
    m_type      = models.CharField('Market Type', max_length=4, null=False)
    chg_date    = models.DateField('Change Date', null=False, auto_now=True)
    t_volume    = models.FloatField('Number of Listed Stocks', null=False)
    data_size   = models.IntegerField('Data Size', null=True)

    class Meta:
        ordering = ['com_code']

    def __init__(self,
                 id, com_code, com_name, m_type,
                 chg_date=None, t_volume=0., data_size=0,
                 *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)

        self.id         = id
        self.com_code   = com_code
        self.com_name   = com_name
        self.m_type     = m_type
        self.chg_date   = chg_date
        self.t_volume   = t_volume
        self.data_size  = data_size

    def __str__(self):
        return f'Company(id={self.id}, ' \
               f'code_code={self.com_code}, com_name={self.com_name}, ' \
               f'm_type={self.m_type}, chg_date={self.chg_date}, ' \
               f't_volume={self.t_volume}, data_size={self.data_size})'


class MarketData(models.Model):

    date        = models.DateField('Trading Date', null=False, db_index=True)
    com_code    = models.CharField('Company Code', max_length=7, null=False, db_index=True)
    com_name    = models.CharField('Company Name', max_length=500, null=False)
    m_type      = models.CharField('Market Type', max_length=4, null=False)
    open        = models.FloatField('Open Price', null=False)
    low         = models.FloatField('Low Price', null=False)
    high        = models.FloatField('High Price', null=False)
    close       = models.FloatField('Close Price', null=False)
    diff        = models.FloatField('Difference Price', null=False)
    ratio       = models.FloatField('Difference Ratio', null=False)
    volume      = models.FloatField('Volume', null=False)
    value       = models.FloatField('Trading Value', null=False)
    t_volume    = models.FloatField('Number of Listed Stocks', null=False)
    t_value     = models.FloatField('Total Value', null=False)

    class Meta:
        ordering = ['-date', 'com_code']

    def __init__(self,
                 id, date, com_code, com_name, m_type,
                 open, low, high, close, diff, ratio,
                 volume, value, t_volume, t_value, *args, **kwargs):
        super(MarketData, self).__init__(*args, **kwargs)

        self.id         = id
        self.date       = date
        self.com_code   = com_code
        self.com_name   = com_name
        self.m_type     = m_type
        self.open       = open
        self.low        = low
        self.high       = high
        self.close      = close
        self.diff       = diff
        self.ratio      = ratio
        self.volume     = volume
        self.value      = value
        self.t_volume   = t_volume
        self.t_value    = t_value

    def __str__(self):
        return f'MarketData(id={self.id}, ' \
               f'date={self.date}, com_code={self.com_code}, ' \
               f'prices=[{self.open}/ {self.low}/ {self.high}/ {self.close}], ' \
               f'diff={self.diff}, ratio={self.ratio}, ' \
               f'volume={self.volume}, value={self.value}, ' \
               f't_volume={self.t_volume}, t_value={self.t_value})'


class ModelingData(models.Model):

    date        = models.DateField('Trading Date', null=False, db_index=True)
    com_code    = models.CharField('Company Code', max_length=7, null=False, db_index=True)
    open        = models.FloatField('Open Price', null=False)
    low         = models.FloatField('Low Price', null=False)
    high        = models.FloatField('High Price', null=False)
    close       = models.FloatField('Close Price', null=False)
    volume      = models.FloatField('Volume', null=False)

    class Meta:
        ordering = ['-date']

    def __init__(self,
                 id, date, com_code, open, low, high, close, volume,
                 *args, **kwargs):
        super(ModelingData, self).__init__(*args, **kwargs)

        self.id         = id
        self.date       = date
        self.com_code   = com_code
        self.open       = open
        self.low        = low
        self.high       = high
        self.close      = close
        self.volume     = volume


    def __str__(self):
        return f'ModelingData(id={self.id}, date={self.date}, ' \
               f'com_code={self.com_code}, ' \
               f'prices=[{self.open}/ {self.low}/ {self.high}/ {self.close}], ' \
               f'volume={self.volume})'


class ModelingInfo(models.Model):

    date        = models.DateField('Modeling Date', null=False, db_index=True)
    com_code    = models.CharField('Company Code', max_length=7, null=False, db_index=True)
    r_open      = models.FloatField('Real Today Open Price', null=True)
    r_close     = models.FloatField('Real Today Close Price', null=True)
    p_open      = models.FloatField('Predict Open Price', null=True)
    p_close     = models.FloatField('Predict Close Price', null=True)
    o_ratio     = models.FloatField('Open Price Ratio', null=True)
    c_ratio     = models.FloatField('Close Price Ratio', null=True)
    p_ratio     = models.FloatField('Predict Open-Close Price Ratio', null=True)
    accuracy    = models.FloatField('Test Accuracy', null=True)

    class Meta:
        ordering = ['-date']

    def __init__(self,
                 id, date, com_code,
                 r_open=None, r_close=None, p_open=None, p_close=None,
                 o_ratio=None, c_ratio=None, p_ratio=None, accuracy=None,
                 *args, **kwargs):
        super(ModelingInfo, self).__init__(*args, **kwargs)

        self.id         = id
        self.date       = date
        self.com_code   = com_code
        self.r_open     = r_open
        self.r_close    = r_close
        self.p_open     = p_open
        self.p_close    = p_close
        self.o_ratio    = o_ratio
        self.c_ratio    = c_ratio
        self.p_ratio    = p_ratio
        self.accuracy   = accuracy

    def __str__(self):
        return f'ModelingInfo(id={self.id}, date={self.date}, ' \
               f'com_code={self.com_code}, ' \
               f'real data=[open={self.r_open}, close={self.r_close}], ' \
               f'predict data=[open={self.p_open}, close={self.p_close}], ' \
               f'ratio=[open={self.o_ratio}, close={self.c_ratio}, close/open={self.p_ratio}], ' \
               f'accuracy={self.accuracy})'


class ModelInfo(models.Model):

    model_name  = models.CharField('Model Name', max_length=100, null=False)
    com_code    = models.CharField('Company Code', max_length=7, default='000000')
    date        = models.DateField('Training Date', null=False, db_index=True)
    info        = models.JSONField('Model Create Info', default={})
    model_path  = models.CharField('Model File Path', max_length=300, null=False)
    max_value   = models.FloatField('Max Value', null=True)
    accuracy    = models.FloatField('Model Accuracy', null=True)

    class Meta:
        ordering = ['model_name', '-date']

    def __init__(self,
                 id, model_name, com_code, date, info, model_path,
                 max_value=0., accuracy=0.,
                 *args, **kwargs):
        super(ModelInfo, self).__init__(*args, **kwargs)

        self.id         = id
        self.model_name = model_name
        self.com_code   = com_code
        self.date       = date
        self.info       = info
        self.model_path = model_path
        self.max_value  = max_value
        self.accuracy   = accuracy

    def __str__(self):
        return f'ModelInfo(id={self.id}, ' \
               f'model_name={self.model_name}, com_code={self.com_code}, ' \
               f'date={self.date}, info=[{self.info}], ' \
               f'model_path={self.model_path}, ' \
               f'max_value={self.max_value}, accuracy={self.accuracy})'


class MyTrading(models.Model):

    date        = models.DateField('Trading Date', null=False, db_index=True)
    com_code    = models.CharField('Company Code', max_length=7, null=False, db_index=True)
    t_type      = models.CharField('Trading Type', max_length=4, null=False)
    t_count     = models.IntegerField('Trading Count', null=False)
    p_close     = models.FloatField('Predict Close Price', null=True)
    buy_price   = models.FloatField('Buy Price')
    sell_price  = models.FloatField('Sell Price')
    ratio       = models.FloatField('Ratio')
    volume      = models.FloatField('Trading Volume')
    profit      = models.FloatField('Trading Profit')

    class Meta:
        ordering = ['-date', 'com_code']

    def __init__(self,
                 id, date, com_code, t_type, t_count, p_close=0.,
                 buy_price=0, sell_price=0, ratio=.0,
                 volume=0, profit=.0,
                 *args, **kwargs):
        super(MyTrading, self).__init__(*args, **kwargs)

        self.id         = id
        self.date       = date
        self.com_code   = com_code
        self.t_type     = t_type
        self.t_count    = t_count
        self.p_close    = int(p_close)
        self.buy_price  = buy_price
        self.sell_price = sell_price
        self.ratio      = ratio
        self.volume     = volume
        self.profit     = profit

    def __str__(self):
        return f'MyTrading(id={self.id}, date={self.date}, com_code={self.com_code}, ' \
               f't_type/count=[{self.t_type}/{self.t_count}], p_close={self.p_close}, ' \
               f'price=[buy={self.buy_price}, sell={self.sell_price}], ' \
               f'ratio={self.ratio}, volume={self.volume}, profit={self.profit})'


class Account(models.Model):

    acc_name    = models.CharField('Account Name', max_length=20, null=False, unique=True)
    t_type      = models.CharField('Trading Type', max_length=4, null=False)
    t_count     = models.IntegerField('Trading Count', null=False)
    base_money  = models.FloatField('Base Money', null=False)
    balance     = models.FloatField('Current Balance', null=True)
    ratio       = models.FloatField('Ratio', null=True)
    first_date  = models.DateField('First Trading Date', auto_now_add=True) # 레코드 생성시 한번 갱신
    last_date   = models.DateField('Last Trading Date', auto_now=True)      # 레코드 변경시 자동 갱신

    class Meta:
        ordering = ['t_type', 't_count']

    def __init__(self,
                 id, acc_name, t_type, t_count, base_money,
                 balance=.0, ratio=.0, first_date=None, last_date=None,
                 *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)

        self.id         = id
        self.acc_name   = acc_name
        self.t_type     = t_type
        self.t_count    = t_count
        self.base_money = base_money
        self.balance    = balance
        self.ratio      = ratio
        self.first_date = first_date
        self.last_date  = last_date

    def __str__(self):
        return f'Account(id={self.id}, acc_name={self.acc_name}, ' \
               f'trading type={self.t_type}, trading count={self.t_count}, ' \
               f'base_money={self.base_money}, ' \
               f'balance={self.balance:,.0}, ratio={self.ratio:.0}, ' \
               f'first_date={self.first_date}, last_date={self.last_date})'