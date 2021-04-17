import os
import re
import shutil
import traceback
from datetime import datetime

from config.sysfiles.parameter import *


class DataConverter:

    @staticmethod
    def other_to_dict(data):
        data_type = str(type(data))
        chg_data = data
        if 'DataFrame' in data_type:
            chg_data = data.to_dict('records')[0]
        elif 'Series' in data_type:
            chg_data = data.to_dict()
        elif 'models' in data_type:
            chg_data = data.__dict__
        else:
            Logger.info(f'Unsupported data type: type({data_type})')
        return chg_data


class DateTime:

    @staticmethod
    def get_days(period):
        try:
            days = (period['end'] - period['start']).days + 1
        except Exception as e:
            Logger.error(e)
            days = None
        return days


class StartEndLogging(object):

    def __init__(self):
        self._start = datetime.now()
        self._call_func = re.findall('.*/([\w_\-\.]+).* (.*)',
                                     traceback.format_stack()[-3])
        try:
            self._func_msg = f'{self._call_func[0][0]} {self._call_func[0][1]} '
        except:
            self._func_msg = ' '
        Logger.info(f'{self._func_msg} started - {self._start}', is_trace=False)

    def end(self):
        end_dt = datetime.now()
        Logger.info(f'{self._func_msg} ended - {end_dt}, '
                    f'total processing time: {end_dt - self._start}', is_trace=False)


class Logger:

    @staticmethod
    def __log_writer(label, msg, is_trace=True):
        if IS_WRITE(label):
            if is_trace:
                call_trace = re.findall('.*/([\w_\-\.]+).* (.*)',
                                        traceback.format_stack()[-3])
                try:
                    trace_msg = f'{call_trace[0][0]} {call_trace[0][1]} - '
                except:
                    trace_msg = ''
            else:
                trace_msg = ''
            Logger.__file_checker()
            with open(LOG_FILE_PATH, 'a') as logfile:
                logfile.write(f'{datetime.now():%Y-%m-%d %H:%M:%S} '
                              f'[{label.upper():>8}] {trace_msg}'
                              f'{msg}\n')

    @staticmethod
    def __file_checker():
        _DEFAULT_LOG_SIZE = 52428800    # 50M
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH, exist_ok=True)
        try:
            f_size = os.path.getsize(LOG_FILE_PATH)
            try:
                max_size = ByteSize[LOG_FILE_SIZE[-1:]].value * int(LOG_FILE_SIZE[:-1])
            except:
                max_size = _DEFAULT_LOG_SIZE
            if f_size > max_size:
                Logger.__logfile_move()
        except:
            Logger.__logfile_create()

    @staticmethod
    def __logfile_create():
        logfile = open(LOG_FILE_PATH, 'w')
        logfile.close()

    @staticmethod
    def __logfile_move():
        _LOG_FILE_MAX_COUNT = 9999
        log_file_cnt = 0
        max_log_file_cnt = min(_LOG_FILE_MAX_COUNT, LOG_FILE_COUNT)
        min_ctime, max_ctime = float('inf'), float('-inf')
        min_file_name, max_file_name = '', ''
        for file_name in os.listdir(LOG_PATH):
            if re.findall(LOG_FILE_NAME_PREFIX + '\-\d{5}\.log', file_name):
                log_file_cnt += 1
                curr_ctime = os.path.getctime(os.path.join(LOG_PATH, file_name))
                if min_ctime > curr_ctime:
                    min_ctime = curr_ctime
                    min_file_name = file_name
                if max_ctime < curr_ctime:
                    max_ctime = curr_ctime
                    max_file_name = file_name

        if log_file_cnt >= max_log_file_cnt:
            os.remove(os.path.join(LOG_PATH, min_file_name))

        if log_file_cnt == 0:
            new_file_number = 0
        else:
            new_file_number = int(re.findall('\d{5}', max_file_name)[0])
            if new_file_number >= _LOG_FILE_MAX_COUNT:
                new_file_number = 0
            else:
                new_file_number += 1
        new_log_file_name = f'{LOG_FILE_NAME_PREFIX}-{new_file_number:05d}.log'
        shutil.move(LOG_FILE_PATH, os.path.join(LOG_PATH, new_log_file_name))

        Logger.__logfile_create()


    @staticmethod
    def debug(msg, is_trace=True):
        Logger.__log_writer('debug', msg, is_trace=is_trace)

    @staticmethod
    def info(msg, is_trace=True):
        Logger.__log_writer('info', msg, is_trace=is_trace)

    @staticmethod
    def warning(msg, is_trace=True):
        Logger.__log_writer('warning', msg, is_trace=is_trace)

    @staticmethod
    def error(msg, is_trace=True):
        Logger.__log_writer('error', msg, is_trace=is_trace)

    @staticmethod
    def critical(msg, is_trace=True):
        Logger.__log_writer('critical', msg, is_trace=is_trace)