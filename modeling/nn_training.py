import os
from datetime import datetime
from django_pandas.io import read_frame

import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split

from config.sysfiles.parameter import *
from trading.utils import Logger as log
from modeling.utils import Modeling as ml
from modeling.nn_models import lstm
from stock.wrapper import CompanyWrapper as scw
from stock.wrapper import ModelInfoWrapper as smw
from stock.wrapper import ModelingDataWrapper as smlw
from stock.wrapper import ModelingInfoWrapper as smiw


class LstmTraining(object):

    def __init__(self, com_code, kwargs):
        self.model_info = {
            'com_code': com_code,
            'date': smlw.get_date()
        }
        self.etc_info = {}
        self.kwargs = kwargs
        self.kwargs['modeling_info']['window_size'] = self.kwargs['window_size']
        self.is_skip = {'trend': False, 'accuracy': False}

    def preprocessing(self):
        data_df = read_frame(smlw.gets('date', com_code=self.model_info['com_code']))
        self.model_info['r_open'] = float(data_df[-1:]['open'])
        self.model_info['r_close'] = float(data_df[-1:]['close'])
        self.etc_info['max_price'] = ml.get_max_value(data_df[PRICE_COLUMNS])
        self.etc_info['max_volume'] = ml.get_max_value(data_df['volume'])
        self.etc_info['data_size'] = len(data_df)

        data_df[PRICE_COLUMNS] = ml.normalization_nega1_to_posi1(data_df[PRICE_COLUMNS])
        data_df['volume'] = ml.normalization_nega1_to_posi1(data_df['volume'])

        puri_data = {
            'soc_x' : data_df[MODELING_COLUMNS].values.tolist(),
            'soc_yo': data_df['open'].values.tolist(),
            'soc_yc': data_df['close'].values.tolist(),
            'win_x' : [],
            'win_yo': [],
            'win_yc': [],
        }
        window_size = self.kwargs['window_size']
        loop_cnt = (self.etc_info['data_size'] - window_size) - 1
        for i in range(loop_cnt):
            puri_data['win_x'].append(puri_data['soc_x'][i:i+window_size])
            puri_data['win_yo'].append(puri_data['soc_yo'][i+window_size])
            puri_data['win_yc'].append(puri_data['soc_yc'][i+window_size])

        train, test = {}, {}
        train['x'], test['x'], train['yo'], test['yo'], train['yc'], test['yc'] = \
            train_test_split(puri_data['win_x'], puri_data['win_yo'], puri_data['win_yc'],
                             test_size=self.kwargs['test_ratio'], shuffle=False)
        return train, test

    def collbacks(self, monitor):
        early_stopping = EarlyStopping(monitor=monitor, patience=10)

        curr_model_save_path = os.path.join(self.kwargs['model_save_path'],
                                            self.kwargs['model_name'],
                                            str(datetime.now().date()))
        if not os.path.exists(curr_model_save_path):
            os.makedirs(curr_model_save_path, exist_ok=True)
        self.etc_info['model_file_name'] = \
            os.path.join(curr_model_save_path, f'{self.model_info["com_code"]}_model.ckpt')
        check_point = ModelCheckpoint(self.etc_info['model_file_name'],
                                      save_best_only=True, save_weights_only=True,
                                      monitor=monitor, verbose=1)
        return early_stopping, check_point

    def training(self, train_data, validation_data):
        model = lstm(self.kwargs['modeling_info'])
        model.fit(train_data[0], train_data[1],
                  validation_data=(validation_data[0], validation_data[1]),
                  epochs=self.kwargs['modeling_info']['epochs'],
                  batch_size=self.kwargs['modeling_info']['batch_size'],
                  callbacks=[self.collbacks(monitor='val_loss')])
        return model

    def modeling(self):
        train, test = self.preprocessing()
        model = self.training([train['x'], train['yc']], [test['x'], test['yc']])
        model.load_weights(self.etc_info['model_file_name'])
        pred_yc = model.predict(test['x'])
        self.model_info['accuracy'] = ml.accuracy_trend(test['yc'], pred_yc)
        self.model_info['p_close'] = float(pred_yc[-1] * self.etc_info['max_price'])


        if self.model_info['accuracy'] < .5:
            # log.debug(f'accuracy skip: {self.model_info["accuracy"]}')
            self.is_skip['accuracy'] = True
        elif self.model_info['p_close'] < self.model_info['r_close']:
            # log.debug(f'{self.model_info["com_code"]}, '
            #           f'trend skip: p_value({self.model_info["p_close"]}), '
            #           f'r_value({self.model_info["r_close"]})')
            self.is_skip['trend'] = True
        else:
            model2 = self.training([train['x'], train['yo']], [test['x'], test['yo']])
            model2.load_weights(self.etc_info['model_file_name'])
            pred_yo = model2.predict(test['x'])
            self.model_info['p_open'] = float(pred_yo[-1] * self.etc_info['max_price'])
            model_info = ml.cal_ratio(self.model_info)
            smiw.insert(model_info)

        return self.is_skip

    def modeling2(self):
        try:
            train, test = self.preprocessing()
            model = self.training([train['x'], train['yc']], [test['x'], test['yc']])
            model.load_weights(self.etc_info['model_file_name'])
            pred_yc = model.predict(test['x'])
            self.model_info['accuracy'] = ml.accuracy_trend(test['yc'], pred_yc)
            self.model_info['p_close'] = float(pred_yc[-1] * self.etc_info['max_price'])
            self.model_info['p_ratio'] = self.model_info['p_close'] / self.model_info['r_close']
            if self.model_info['accuracy'] < .5:
                self.is_skip['accuracy'] = True
            elif self.model_info['p_close'] < self.model_info['r_close']:
                self.is_skip['trend'] = True
            else:
                smiw.insert(self.model_info)
        except Exception as e:
            raise Exception(e)

        return self.is_skip

    def modeling3(self):
        try:
            train, test = self.preprocessing()
            model = self.training([train['x'], train['yc']], [test['x'], test['yc']])
            model.load_weights(self.etc_info['model_file_name'])
            pred_yc = model.predict(test['x'])
            log.debug(self.kwargs['modeling_info'])
            model_info = {
                'model_name'    : self.kwargs['model_name'],
                'com_code'      : self.model_info['com_code'],
                'date'          : self.model_info['date'],
                'info'          : self.kwargs['modeling_info'],
                'model_path'    : self.etc_info['model_file_name'],
                'max_value'     : self.etc_info['max_price'],
                'accuracy'      : ml.accuracy_trend(test['yc'], pred_yc)
            }
            smw.insert(model_info)
        except Exception as e:
            raise Exception(e)
