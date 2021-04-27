import os
import sys
import numpy as np
from datetime import datetime

from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint


class Modeling:

    @staticmethod
    def accuracy_trend(real, pred):
        """
        시계열 데이터의 예측값과 실제값을 이용해 증가/감소 추세를 맞춘 정확도를 계산한다.
         - 추세: 예측값에서 이전 단계 실제값의 증가/감소 여부와,
                실제값에서 이전 단계 실제값의 증가/감소가 일치하는지 여부 확인
        :param real: 실제값 (list)
        :param pred: 예측값 (list)
        :return: 증가/감소 추세 정확도
        """
        accurate_cnt, inaccurate_cnt = 0, 0
        chk_data_size = len(real)
        for idx in range(chk_data_size-1):
            next_idx = idx + 1
            if pred[next_idx] == real[next_idx]:
                accurate_cnt += 1
            else:
                if pred[next_idx] - real[idx] > 0:
                    if real[next_idx] - real[idx] > 0:
                        accurate_cnt += 1
                    else:
                        inaccurate_cnt += 1
                else:
                    if real[next_idx] - real[idx] > 0:
                        inaccurate_cnt += 1
                    else:
                        accurate_cnt += 1
        return accurate_cnt / (chk_data_size-1)


    @staticmethod
    def get_max_value(datas, is_abs=True):
        datas_type = str(type(datas))
        try:
            if is_abs:
                datas = np.abs(datas)
            if 'DataFrame' in datas_type:
                max_value = np.max(list(np.max(datas)))
            elif 'Series' in datas_type:
                max_value = np.max(list(datas))
            elif 'list' in datas_type:
                max_value = np.max(datas)
            else:
                raise Exception(f'get_max_value unsupported data type - {datas_type}')
        except Exception as e:
            raise Exception(e)
        return max_value


    @staticmethod
    def normalization_nega1_to_posi1(datas):
        return datas / Modeling.get_max_value(datas)


    @staticmethod
    def cal_ratio(modelinfo_dt):
        try:
            modelinfo_dt['o_ratio'] = modelinfo_dt['p_open'] / modelinfo_dt['r_open']
            modelinfo_dt['c_ratio'] = modelinfo_dt['p_close'] / modelinfo_dt['r_close']
            modelinfo_dt['p_ratio'] = modelinfo_dt['p_open'] /modelinfo_dt['p_close']
        except:
            modelinfo_dt['o_ratio'], modelinfo_dt['c_ratio'], modelinfo_dt['p_ratio'] = 0., 0., 0.
        return modelinfo_dt