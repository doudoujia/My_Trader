# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 17:29:38 2018

@author: gli26
"""

from my_trader import *
from my_strategies import *

robinhood = get_robinhood()


stocks, quantity = robinhood.get_my_positions()

plot_position(stocks,quantity)
robinhood.logout()