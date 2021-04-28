import os
import platform
import tensorflow as  tf
from enum import Enum, IntEnum

_PROJECT_NAME = 'MyTrading'
_USER_PATH = os.path.expanduser('~')

_PROJECT_BASE = os.path.join(_USER_PATH, 'projects')
_PROJECT_PATH = os.path.join(_PROJECT_BASE, _PROJECT_NAME)
_PROJECT_SYSFILE_PATH = os.path.join(_PROJECT_PATH, 'config', 'sysfiles')

_DATA_PATH = os.path.join(_PROJECT_BASE, 'Data')

if 'Windows' in platform.platform():
    WEB_DRIVER_PATH = os.path.join(_USER_PATH, '.local', 'bin', 'chromedriver.exe')
else:
    WEB_DRIVER_PATH = os.path.join(_USER_PATH, '.local', 'bin', 'chromedriver')
KRX_CRAWLING_URL = 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101'

_CODE_FILE_NAME = 'code.csv'
CODE_FILE_PATH = os.path.join(_PROJECT_SYSFILE_PATH, _CODE_FILE_NAME)


# PROGRAM PARAMETER
SYSTEM_CODE_TYPE = '0'
FIRST_TRADING_DATE = '19950502'
BASE_TRADING_DATE = '20000529'
BASE_CRAWLING_TIME = '17:00:00'
DOWNLOAD_WATING_TIME_BEFORE_BASE_TIME = 6  # 장중
DOWNLOAD_WATING_TIME_AFTER_BASE_TIME = 3   # 폐장 후

COLUMN_NAMES = ['com_code', 'com_name', 'm_type', 'm_dept',
                'close', 'diff', 'ratio', 'open', 'high', 'low', 'volume',
                'value', 't_value', 't_volume']

# PRE-PROCESSING PARAMETER
TOTAL_CHECK_MAX_RATIO = 2.
TOTAL_CHECK_MIN_RATIO = .5
DAY_CHECK_MAX_RATIO = 1.5
DAY_CHECK_MIN_RATIO = .6

# MODELING PARAMETER
MODELING_WINDOW_SIZE = 10
MODELING_SKIP_DATA_SIZE = 4000
TRAIN_DATA_RATIO = .8
PRICE_COLUMNS = ['open', 'low', 'high', 'close']
MODELING_COLUMNS = PRICE_COLUMNS + ['volume']
MODEL_SAVE_PATH = os.path.join(_DATA_PATH, 'models', _PROJECT_NAME)

# LSTM MODEL PARAMETER
LSTM_MODEL_NAME = 'LSTMClassifier'
LSTM_START_UNIT = 100
LSTM_MID_UNIT = 100
LSTM_AF = 'relu'
LSTM_DROPOUT_RATIO = .1
LSTM_OUTPUT_UNIT = 1

# LOGGER SETTING
class LogLabel(IntEnum):
    debug       = 1
    info        = 2
    warning     = 3
    error       = 4
    critical    = 5
LOG_LABEL = 'debug'
IS_WRITE = lambda x: LogLabel[x] >= LogLabel[LOG_LABEL]
LOG_PATH = os.path.join(_DATA_PATH, 'logs', _PROJECT_NAME)
LOG_FILE_NAME_PREFIX = f'{_PROJECT_NAME}'
LOG_FILE_NAME = f'{LOG_FILE_NAME_PREFIX}.log'
LOG_FILE_PATH = os.path.join(LOG_PATH, LOG_FILE_NAME)
LOG_FILE_SIZE = '100M'
LOG_FILE_COUNT = 10

# DBMS PARAMETER
BULK_DATA_SIZE = 5000
MIN_BULK_DATA_SIZE = 500

# CRAWLING PARAMETER
_CRAWLING_PATH = os.path.join(_DATA_PATH, 'crawling', 'krx')
CRAWLING_DOWNLOAD_PATH = os.path.join(_USER_PATH, 'download')
CRAWLING_TARGET_PATH = os.path.join(_CRAWLING_PATH, 'original')
CRAWLING_BACKUP_PATH = os.path.join(_CRAWLING_PATH, 'backup')
_MERGE_FILE_NAME = 'merge.csv'
CRAWLING_MERGE_FILE_PATH = os.path.join(_CRAWLING_PATH, 'merge', _MERGE_FILE_NAME)

# TRADING PARAMETER
TRADING_MIN_COUNT = 1
TRADING_MID_COUNT = 3
TRADING_MAX_COUNT = 5

## ETC PARAMETER
# 일단위로 MarketData에서 ModelingData로 데이터를 옮기는 최대 일자 지정
# 이 일자보다 큰 경우 ModelingData를 초기화하는 프로세스 수행
MTM_MAX_DAYS = 30

class ByteSize(Enum):
    K = 1024
    M = 1024 * 1024
    G = 1024 * 1024 * 1024
    T = 1024 * 1024 * 1024 * 1024


# Modeling Parameter
LSTM_KWARGS = {
    'window_size'       : MODELING_WINDOW_SIZE,
    'test_ratio'        : 1. - TRAIN_DATA_RATIO,
    'model_save_path'   : MODEL_SAVE_PATH,
    'modeling_info'     : {
        'feature_size'  : len(MODELING_COLUMNS),
        'epochs'        : 60,
        'batch_size'    : 30,
        'input_units'   : 100,
        'middle_units'  : 100,
        'output_units'  : 1,
        'activation_fn' : 'relu',
        'dropout'       : .1,
        'loss'          : 'mean_squared_error',
        'optimizer'     : tf.keras.optimizers.Adam(.0005),
        'metrics'       : 'mse'
    }
}
