import os
import sys
import pandas as pd

from stock.models import Code, Company, MarketData, ModelingData, ModelingInfo, MyTrading, Account
from config.sysfiles.parameter import *


class CodeWrapper:

    @staticmethod
    def init():
        Code.objects.all().delete()

        code_df = pd.read_csv(CODE_FILE_PATH, delimiter=',', encoding='utf-8')