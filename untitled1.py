# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 10:58:07 2018

@author: gli26
"""

from my_trader import *

robinhood = get_robinhood()

#print robinhood.my_trader.portfolios()["last_core_equity"]
#print beta(["WLK"],interval="day")
#print robinhood.hedge("SH",0.3)
update_price()
#update_fundamentals(skip_can=True)
robinhood.logout()