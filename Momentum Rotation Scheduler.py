
from my_trader import *

import time
import timeit
import talib as ta
import numpy as np
from Robinhood import Robinhood

import xlrd
from datetime import datetime
from pandas_datareader import data as da
import schedule


if datetime.now().weekday() == 0:
    last_trade_date_count = 3
elif datetime.now().weekday() == 6:
    last_trade_date_count = 2
else:
    last_trade_date_count = 1


directory = "file/"
working_suggestion = "Trade_suggestion_robinhood_1st"
stock_suggestion_path = directory + working_suggestion + str(datetime.now()-timedelta(days=last_trade_date_count))[0:10]+".csv"



#Template

# =============================================================================
# flag = False
# trail = 0
# while not flag and trail > 3:
#     try:
#
#         flag = True
#     except Exception as e:
#         print (e);
#         trail += 1
#         continue
# =============================================================================


class bot:
    
    def __init__(self):
        self.can_trade = False
        
        trail = 0 
        while not self.can_trade and trail < 3:
            try:
                self.robinhood = get_robinhood()
                self.robinhood.logout()
                self.robinhood.my_trader.login_prompt()
                self.tickers , self.quantity = self.robinhood.get_my_positions()
                print "logined"
                self.can_trade = True
            except Exception as e:
                print e
                self.robinhood.logout()
                trail += 1
                continue
        
        #run check
        test1 = pd.read_csv(directory + "my_universe_industry_sector_marketcap_earnings" + ".csv")
        test1 = test1.dropna()
        print "fundamental content:"
        print test1.columns
        print "Length: ", len(test1)
        if  'Industry'and  'Sector' and 'Market_cap' in test1.columns :
            self.can_trade = True
        else:
            print "fundamental file not complete!"
        if len(test1) > 2000:
            self.can_trade = True
        
        time.sleep(2)
        
        update_price(method="robinhood",test=True)
        
        test1 = pd.read_csv(directory + working_suggestion  + str(datetime.now()-timedelta(days=last_trade_date_count))[0:10]+".csv")
        test1 = test1.dropna()
        print "suggestion content:"
        print "Date: ", test1.TimeStamp[0]
        print test1.columns
        print "Length: ", len(test1)
        
        time.sleep(2)
        
        if not ( 'Industry_weight' and  'Technical_points' and 'Close' in test1.columns ):
            self.can_trade = False
            print "suggestion file not complete"
        if len(test1) < 7:
            self.can_trade = False
    

        time.sleep(2)
        
        self.sell_and_buy()
        
        time.sleep(2)
        self.robinhood.my_trader.cancel_open_orders()
        print "Order all canceled"
        print ""
        
        

        print "Can Trade ",self.can_trade      
        
        if self.can_trade:
            print "******************************************"
            print "***********Ready To Trade*****************"
            print "******************************************"

    def __exit__(self):
        self.robinhood.logout
        print "logouted"



    def update_price(self):

        update_price(method="robinhood")




    def place_my_order_check(self):
       # robinhood = get_robinhood()
        #robinhood.logout()
        #robinhood.login("lgyhz123","5093945464lgyhz")
        
        get_stock = False
        place_order = False
        trail = 0
        while (not get_stock and not place_order) and trail < 3:
            try:
                my_stock = pd.read_csv(stock_suggestion_path)
                my_stock = my_stock.rename(columns={"Unnamed: 0":"Ticker"})
                print ("Get suggestion succeed!")
                get_stock=True
            except:
                print ("Get suggestion fail, stopping")
                trail += 1
                continue
            try:
                my_stock["position_place_quantity"]= np.ceil(((100/len(my_stock.Close))/my_stock.Close))
                power = self.robinhood.get_buying_power()
                self.robinhood.place_buy_bulk_checkup(my_stock.Ticker, my_stock.position_place_quantity)
                if np.dot(my_stock.position_place_quantity,my_stock.Close) < power:
                    print ("Enough buying power")
                    self.robinhood.place_buy_bulk_checkup(my_stock.Ticker, my_stock.position_place_quantity)
                    place_order = True
                else:
                    print ("Not enough buying power")
                    raise
            except Exception, e:
                print e
                trail += 1
#        try:         
#            self.robinhood.get_my_position_beta()
#            my_positions, position_quantity= self.robinhood.get_my_positions()
#            plot_position( my_positions, position_quantity )
#        except Exception, e:
#            print e  
     
#    def hedge(self,hedge_int = "UVXY"):
#        
#        hedge_int_beta =beta([hedge_int],interval ="minute")[0].iloc[0][0]
#        hedge_int_price = robinhood.get_ask_price(hedge_int)
#        position_beta = robinhood.get_my_position_beta_minute()[0]
#        position_value = robinhood.my_trader.market_value()
#        shares = abs(np.floor(position_value*position_beta/hedge_int_beta/hedge_int_price))
#        return shares
        
    def sell_previous_day(self):
        #robinhood = get_robinhood()
        #robinhood.logout()
       # robinhood.my_trader.login("lgyhz123","5093945464lgyhz")
        sell= False
        trail = 0
        while not sell and trail <3:
            try:
                sell_list = self.robinhood.get_last_order_ticker((datetime.now()-timedelta(days=last_trade_date_count)).strftime("%Y-%m-%d"))
                print "sell list"
                print sell_list
                self.robinhood.place_sell_bulk_checkup(sell_list.Ticker,sell_list.Quantity)
                sell = True
               # robinhood.logout()
            except Exception as e:
                print e
                trail += 1
                continue

    def sell_and_buy(self):
        self.sell_previous_day()
        self.place_my_order_check()
        hedge_int = "SH"
        shares = self.robinhood.hedge(hedge_int)
        self.robinhood.place_buy(hedge_int,shares)
        print "################"
        print "Place " + hedge_int + " of " + str(shares) + " to hedge"
        print "\n"
        
    # first, get can_trade universe

    def check_beta(self):
       # robinhood = get_robinhood()
        #robinhood.logout()
        #robinhood.login("lgyhz123","5093945464lgyhz")
        check= False
        trail =0
        while not check and trail <3:
            try:
                self.robinhood.get_my_position_beta_minute()
                check = True
       # robinhood.logout()
            except Exception as e:
                print e
                trail += 1
                continue

        #robinhood.logout()


    def mean_reversion_check(self):
       # robinhood = get_robinhood()
         flag = False
         trail = 0
         while not flag and trail < 3:
             try:
                self.robinhood.get_my_position_beta_minute()
                for i in self.tickers:
                    mean_reversion(self.tickers,"minute")
                flag = True
             except Exception as e:
                 print (e);
                 trail += 1
                 continue
       # robinhood.login("lgyhz123","5093945464lgyhz")

        #robinhood.logout()

    def plot(self):
        #robinhood = get_robinhood()
      #  robinhood.login("lgyhz123","5093945464lgyhz")
         flag = False
         trail = 0
         while not flag and trail < 3:
             try:
                 my_positions, position_quantity= self.robinhood.get_my_positions()
                 print "###################################"
                 print "BETA IS: "
                 print self.robinhood.get_protfolio(my_positions, position_quantity,interval = "minute")[1]
                 print "###################################"
                 plot_position( my_positions, position_quantity )
                 flag = True
             except Exception as e:
                 print (e);
                 trail += 1
                 continue



def hi():
    print (datetime.now())

def bye():
    print ("I am still here")


###########################################################################
#Debug Area:
    
#bot = bot()
#
#bot.place_my_order_check()


###########################################################################
bot = bot()
schedule.clear()
##schedule.every(4).weeks.do(update_fundamentals)
#schedule.every(2).minutes.do(hi)
schedule.every(20).minutes.do(bot.plot)
##schedule.every(25).minutes.do(mean_reversion_check)

schedule.every().monday.at("8:22").do(bot.update_price)
schedule.every().tuesday.at("4:06").do(bot.update_price)
schedule.every().wednesday.at("4:06").do(bot.update_price)
schedule.every().thursday.at("4:06").do(bot.update_price)
schedule.every().friday.at("4:06").do(bot.update_price)


schedule.every().monday.at("8:50").do(bot.sell_and_buy)
schedule.every().tuesday.at("6:01").do(bot.sell_and_buy)
schedule.every().wednesday.at("7:01").do(bot.sell_and_buy)
schedule.every().thursday.at("7:01").do(bot.sell_and_buy)
schedule.every().friday.at("8:45").do(bot.sell_and_buy)

while True:
    schedule.run_pending()

    time.sleep(1)
###########################################################################

