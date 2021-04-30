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
from stock.wrapper import ModelInfoWrapper as smw
from stock.wrapper import ModelingDataWrapper as smlw
from modeling.nn_training import LstmTraining
from modeling.nn_models import lstm


def tensorflow_init():
    gpu = tf.config.experimental.list_physical_devices('GPU')
    try:
        tf.config.experimental.set_memory_growth(gpu[0], True)
    except RuntimeError as e:
        log.error(e)

def lstm_test():
    se = StartEndLogging()

    modeling_target_qs = scw.gets_modeling_target()
    log.info(len(modeling_target_qs))

    cnt_skip_trend, cnt_skip_accuracy = 0, 0
    for modeling_company in modeling_target_qs[:15]:
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


def lstm_test3():
    se = StartEndLogging()

    modeling_target_qs = scw.gets_modeling_target()

    for modeling_company in modeling_target_qs[:10]:
        model = LstmTraining(modeling_company.com_code, LSTM_KWARGS)
        model.modeling3()

    se.end()


def predict():

    try:
        model_info_qs = smw.get_models('LSTM', '2021-04-28')
        for model_info in model_info_qs[:1]:
            data_lst = smlw.get_prediction_datas(model_info.com_code, model_info.date,
                                                 model_info.info['window_size'])
            if data_lst is None:
                continue
            log.warning(f'data_lst type: {type(data_lst)}\n{data_lst}')
            pred_data_lst = data_lst / model_info.max_value
            model = lstm(model_info.info)
            model.load_weights(model_info.model_path)
            pred = model.predict(pred_data_lst)
            log.warning(pred * model_info.max_value)


    except Exception as e:
        raise Exception(e)



if __name__ == '__main__':
    try:
        # tensorflow_init()
        # lstm_test3()
        predict()
    except Exception as err:
        log.error(err)