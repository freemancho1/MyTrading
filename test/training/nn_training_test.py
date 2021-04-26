import os
import sys

project_path = os.path.abspath(__file__+'/../../..')
if project_path not in sys.path:
    sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

import tensorflow as tf

from config.sysfiles.parameter import *
from trading.utils import Logger as log
from trading.utils import StartEndLogging
from stock.wrapper import CompanyWrapper as scw
from modeling.nn_training import LstmTraining

kwargs = {
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

def lstm_test():
    se = StartEndLogging()

    modeling_target_qs = scw.gets_modeling_target()
    log.info(len(modeling_target_qs))

    cnt_skip_trend, cnt_skip_accuracy = 0, 0
    for modeling_company in modeling_target_qs[:30]:
        model = LstmTraining(modeling_company.com_code, kwargs)
        is_skip = model.modeling()
        se.mid(f'{modeling_company.com_code}')
        if is_skip['trend']:
            cnt_skip_trend += 1
        if is_skip['accuracy']:
            cnt_skip_accuracy += 1
    log.info(f'modeling total count: {len(modeling_target_qs)}, '
             f'trend skip: {cnt_skip_trend}, accuracy skip: {cnt_skip_accuracy}')

    se.end()



if __name__ == '__main__':
    lstm_test()