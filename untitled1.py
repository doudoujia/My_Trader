# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 10:58:07 2018

@author: gli26
"""

from my_trader import *

mongodb = mongo()
def daily_update_db():
    mongodb = mongo()
    all_stock_data = mongodb.get_all_quote()
    mongodb.update_db(all_stock_data)
#print robinhood.my_trader.portfolios()["last_core_equity"]
#print beta(["WLK"],interval="day")
#print robinhood.hedge("SH",0.3)
daily_update_db()
#pair_trade("AAPL","QSR",1500)

#update_fundamentals(skip_can=True)
#mongodb.query_database("QSR",start_date=datetime.now()-timedelta(days=210),end_date=datetime.now()-timedelta(days=0))