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

def complete_line(pct):
    graph = "->"
    pct *=100
    line_pct = np.ceil(pct/5)
    for i in range(int(line_pct)):
        graph += "->"
#    print (graph + "  " + str(pct) + "%")
    print (graph + "{0:>100.2f}%".format(pct))
    
        

start = timeit.default_timer()
tradeable = pd.read_csv(directory + "cantrade.csv")
start_point=0
tradeable = tradeable[start_point:]
pair=[]
good_pair = []
count = 0
res_total_return=[]
res_ave_return=[]
res_volatility=[]
res_sharp_ratio=[]
pairs=[]
for i in tradeable.Ticker:
     start_point+=1    
     for j in tradeable.Ticker:
        
        count +=1
        if i==j:
            continue
        else:
#            if count %20 ==0:
#                time.sleep(60)
            
            print ("\n")
            print ("***************************")
            print ("Pair {} and {}".format(i,j))
            try:
                temp_price = pair_trade(i,j,1500,continuous=True)
            except KeyError:
                print ("price data not complete")
                continue
            try:
                total_return  = temp_price.p_L.sum()
                ave_return = temp_price.p_L.mean()
                volatility = temp_price.p_L.std()
                sharp_ratio = ave_return/volatility 
                res_total_return.append(total_return)
                res_ave_return.append(ave_return)
                res_volatility.append(volatility)
                res_sharp_ratio.append(sharp_ratio)
                pairs.append((i,j))
                print ("Total return = {}".format(total_return))
                print ("Average return = {}".format(ave_return))
                print ("Volatility = {}".format(volatility))
                print ("Sharp_ratio = {}".format(sharp_ratio))
                if total_return >100 and ave_return > 5:
                    pair.append((i,j))
                if sharp_ratio >1:
                    good_pair.append((i,j))
                if count %100 ==0:
                    final = pd.DataFrame({"pairs":pairs,"total_return":res_total_return,\
    "ave_return":res_ave_return,"volatility":res_volatility,\
    "sharp_ratio":res_sharp_ratio})
                    final.to_csv("pair_trade_BT_ETF.csv")
            except Exception as e:
                print e    
                continue
        complete_line(float(count)/(len(tradeable)*len(tradeable)))
final = pd.DataFrame({"pairs":pairs,"total_return":res_total_return,\
    "ave_return":res_ave_return,"volatility":res_volatility,\
    "sharp_ratio":res_sharp_ratio})
final.to_csv("pair_trade_BT_ETF.csv")
stop = timeit.default_timer()
print ("total time {}".format(stop-start))