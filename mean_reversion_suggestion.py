# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 12:17:48 2018

@author: gli26
"""

from my_lib import *
from my_trader import *
from my_strategies import *
import time
import timeit
import talib as ta
import numpy as np
from Robinhood import Robinhood

import xlrd
from datetime import datetime
from pandas_datareader import data as da
import schedule
from update_price import *
from get_industry_sector_earnings import *


tradeable = pd.read_csv("file/cantrade.csv")
tradeable = tradeable.dropna()
result = pd.DataFrame()
for i in tradeable.Ticker:
    try:
        get = mean_reversion(i,"minute")
        if get[0] != "Augmented Dickey Fuller: Not significant":
            result = result.append(get)
            print "FOUND ",i
    except:
        print "get error"
        continue

result.to_csv("file/mean_reversion_suggestions.csv")
