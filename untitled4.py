# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 17:29:38 2018

@author: gli26
"""

from my_trader import *
#from my_strategies import *

#robinhood = get_robinhood()
#
#
#stocks, quantity = robinhood.get_my_positions()
#
#plot_position(stocks,quantity)
#robinhood.logout()

#update_fundamentals()

start = timeit.default_timer()
tradeable = pd.read_csv(directory + universe_file_name)
tradeable = tradeable[1:]
pair=[]
good_pair = []
count = 0
for i, j in zip(tradeable.Ticker,tradeable.Ticker.shift(-1)):
        
        if i==j:
            continue
        else:
            if count %20 ==0:
                time.sleep(60)
            count +=1
            print ("\n")
            print ("***************************")
            print ("Pair {} and {}".format(i,j))
            temp_price = pair_trade(i,j,1500,continuous=True)
            try:
                total_return  = temp_price.p_L.sum()
                ave_return = temp_price.p_L.mean()
                volatility = temp_price.p_L.std()
                sharp_ratio = ave_return/volatility 
                print ("Total return = {}".format(total_return))
                print ("Average return = {}".format(ave_return))
                print ("Volatility = {}".format(volatility))
                print ("Sharp_ratio = {}".format(sharp_ratio))
                if total_return >100:
                    pair.append((i,j))
                if sharp_ratio >1:
                    good_pair.append((i,j))
            except Exception as e:
                print e
                continue
stop = timeit.default_timer()
print ("total time {}".format(stop-start))