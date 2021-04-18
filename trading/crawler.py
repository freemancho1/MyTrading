import os
import re
import sys
import time
import shutil

import pandas as pd
from selenium import webdriver
from datetime import datetime, timedelta
from dateutil.parser import parse
from tqdm import tqdm

from config.sysfiles.parameter import *
from trading.utils import Logger as log
from trading.utils import StartEndLogging
from stock.wrapper import MarketDataWrapper as smdw


def get_krx_crawling_period(s_date, e_date, is_that_day=False):
    t_date = smdw.get_date(is_add_one=True)
    try:
        if s_date.lower() == 'all':
            cs_date = parse(BASE_TRADING_DATE).date()
        else:
            cs_date = parse(s_date).date()
            if not is_that_day:
                cs_date = max([cs_date, t_date])
    except:
        cs_date = t_date

    today = datetime.now().date()
    curr_time = datetime.now().time()
    try:
        ce_date = parse(e_date).date()
    except:
        ce_date = datetime.now().date()

    if ce_date > today:
        ce_date = today
    elif ce_date == today and curr_time < parse(BASE_CRAWLING_TIME).time():
        ce_date = ce_date - timedelta(days=1)
    ce_date = max([cs_date, ce_date])
    return cs_date, ce_date


class KrxCrawler(object):

    def __init__(self, s_date=None, e_date=None, is_that_day=False, is_insert=True):
        self._web_driver = webdriver.Chrome(WEB_DRIVER_PATH)
        self._web_driver.get(KRX_CRAWLING_URL)
        time.sleep(2)
        self._s_date, self._e_date = get_krx_crawling_period(s_date, e_date, is_that_day)
        self._ws_date, self._we_date = None, None
        self._cnt_work_days = 0
        self._is_start, self._is_stop = True, False
        self._is_insert = is_insert


    def start_crawler(self, is_disp_processing_step=False):
        se_check = StartEndLogging()

        about_period_months = int((self._e_date - self._s_date).days / 30) + 2

        log.info(f'Input days: {self._s_date} ~ {self._e_date} '
                 f'({(self._e_date - self._s_date).days + 1} days)')
        if is_disp_processing_step:
            lists = tqdm(range(about_period_months))
        else:
            lists = range(about_period_months)

        try:
            for _ in lists:
                cnt_work_days, cnt_skip_days = self._go_end_trading_day(not self._is_start) \
                                               if self._is_start else \
                                               self._change_calendar_month()
                if cnt_work_days == 0: break
                prev_work_date = None
                for day_idx in reversed(range(cnt_work_days)):
                    curr_work_day = self._get_day_data(day_idx)
                    self._cnt_work_days += 1
                    if self._we_date is None:
                        self._we_date = parse(curr_work_day).date()
                    self._ws_date = parse(curr_work_day).date()
                    if self._ws_date == self._s_date:
                        self._is_stop = True
                        break
                    if self._ws_date < self._s_date:
                        self._is_stop = True
                        os.remove(os.path.join(CRAWLING_TARGET_PATH, f'{curr_work_day}.csv'))
                        self._ws_date = prev_work_date
                        self._cnt_work_days -= 1
                        break
                    prev_work_date = self._ws_date
                if str(self._ws_date)[:7] == str(self._s_date)[:7]:
                    self._is_stop = True
                if self._is_stop:
                    break
        except Exception as e:
            log.error(e)

        log.info(f'Working days: '
                 f'{self._ws_date} ~ {self._we_date} ({self._cnt_work_days} days)')

        self._web_driver.quit()

        se_check.end()


    def _get_day_data(self, idx):

        self._web_driver.find_element_by_class_name('cal-btn-open').click()
        work_weeks = self._web_driver.find_element_by_class_name('cal-monthly-table') \
                                     .find_elements_by_tag_name('tbody > tr')
        work_days = []
        for work_week in work_weeks:
            for day in work_week.find_elements_by_tag_name('td > a'):
                work_days.append(day)

        work_days[idx].click()
        self._web_driver.find_element_by_id('jsSearchButton').click()
        if datetime.now().time() < parse(BASE_CRAWLING_TIME).time():
            wating_time = DOWNLOAD_WATING_TIME_BEFORE_BASE_TIME
        else:
            wating_time = DOWNLOAD_WATING_TIME_AFTER_BASE_TIME
        time.sleep(wating_time)

        self._web_driver.find_element_by_xpath('//*[@id="MDCSTAT015_FORM"]/div[2]/div/p[2]/button[2]').click()
        self._web_driver.find_elements_by_tag_name('span.ico_filedown')[1].click()
        time.sleep(5)

        curr_work_day = self._web_driver.find_element_by_id('trdDd') \
                                        .get_attribute('value')

        source_file = os.path.join(CRAWLING_DOWNLOAD_PATH,
                                   os.listdir(CRAWLING_DOWNLOAD_PATH)[0])
        target_file = os.path.join(CRAWLING_TARGET_PATH, f'{curr_work_day}.csv')
        shutil.move(source_file, target_file)

        return curr_work_day


    def _go_end_trading_day(self, is_start=True):

        self._web_driver.find_element_by_class_name('cal-btn-open').click()

        if is_start:
            self._web_driver.find_element_by_class_name('cal-btn-prevM').click()

        first_day = self._get_start_trading_day_in_curr_month()
        cnt_diff_days = (self._e_date - first_day).days
        if cnt_diff_days < 0:
            if str(self._e_date)[:7] == str(first_day)[:7]:
                self._e_date = self._e_date.replace(day=1) - timedelta(days=1)
            cnt_work_days, cnt_skip_days = self._go_end_trading_day()
        else:
            self._web_driver.find_element_by_class_name('cal-btn-open').click()
            work_weeks = self._web_driver.find_element_by_class_name('cal-monthly-table') \
                                         .find_elements_by_tag_name('tbody > tr')
            cnt_work_days, cnt_skip_days = 0, 0
            for work_week in work_weeks:
                for work_day in work_week.find_elements_by_tag_name('td > a'):
                    _work_day = int(work_day.text)
                    if _work_day <= self._e_date.day:
                        cnt_work_days += 1
                        if str(self._s_date)[:7] == str(first_day)[:7] \
                            and _work_day < self._s_date.day:
                            cnt_skip_days += 1
                    else:
                        break
            self._web_driver.find_element_by_class_name('cal-btn-open').click()

        self._is_start = False
        return cnt_work_days, cnt_skip_days


    def _change_calendar_month(self):

        self._web_driver.find_element_by_class_name('cal-btn-open').click()
        self._web_driver.find_element_by_class_name('cal-btn-prevM').click()

        work_weeks = self._web_driver.find_element_by_class_name('cal-monthly-table') \
                                     .find_elements_by_tag_name('tbody > tr')
        work_days = []
        for work_week in work_weeks:
            for day in work_week.find_elements_by_tag_name('td > a'):
                work_days.append(day)
        work_days[0].click()

        return len(work_days), 0


    def _get_start_trading_day_in_curr_month(self):

        try:
            # 입력값으로 들어온 마지막 거래일자와 비교하기 위해 해당월 첫째주 첫번째 거래일자를 읽기 위해 클릭한다.
            self._web_driver.find_element_by_class_name('cal-monthly-table') \
                            .find_elements_by_tag_name('tbody > tr')[0] \
                            .find_elements_by_tag_name('td > a')[0].click()
        except:
            # 위에서 해당월 첫째주에 주식 거래일자가 없으면 에러가 발생하기 때문에 둘째주 첫번째 거래일자를 읽기 위해 클릭한다.
            self._web_driver.find_element_by_class_name('cal-monthly-table') \
                            .find_elements_by_tag_name('tbody > tr')[1] \
                            .find_elements_by_tag_name('td > a')[0].click()

        # 클릭된 거래일자의 "일자" 정보를 읽는다.
        first_day = parse(self._web_driver.find_element_by_id('trdDd') \
                                          .get_attribute('value')).date()
        return first_day