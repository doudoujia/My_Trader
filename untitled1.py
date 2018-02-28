# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 10:58:07 2018

@author: gli26
"""

from my_trader import *


def daily_update_db():
    mongodb = mongo()
    all_stock_data = mongodb.get_all_quote()
    mongodb.update_db(all_stock_data)
#print robinhood.my_trader.portfolios()["last_core_equity"]
#print beta(["WLK"],interval="day")
#print robinhood.hedge("SH",0.3)
daily_update_db()
#update_fundamentals(skip_can=True)
