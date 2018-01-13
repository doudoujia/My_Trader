
import time
import timeit
import talib as ta
import numpy as np
from Robinhood import Robinhood
from pandas import *
import xlrd
import  talib as ta
from datetime import datetime
from pandas_datareader import data as da
import pandas as pd
import numpy as np
from numpy import log, polyfit, sqrt, std, subtract
import statsmodels.tsa.stattools as ts
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import pprint
from datetime import timedelta

def beta(ticker_list,bench = "SPY"):    
    # will return a dataframe
    betas = []
    
    ben_mark= da.DataReader(bench,"yahoo",datetime.now()-timedelta(days=90),datetime.now())
    for i in list(ticker_list):
        ticker = i
        try:
            stock = da.DataReader(str(ticker),"yahoo",datetime.now()-timedelta(days=90),datetime.now())
        except:
            print (str(i)+" ticker maybe wrong. Error in getting data from yahoo")
            betas.append(np.NaN)
            continue

        # get return and put them in a new dataframe

        ben_mark=ben_mark.rename(columns ={"Adj Close":bench})
        stock = stock.rename(columns = {"Adj Close":ticker})
        ben_mark[bench + "_re"] = log(ben_mark[bench]/ben_mark[bench].shift(1))
        stock[ticker + "_re"] = log(stock[ticker]/stock[ticker].shift(1))
        new = pd.concat([ben_mark,stock],axis =1)
        new = new[[bench,bench + "_re",ticker, ticker + "_re" ]]
        new = new.dropna()

        #calculate beta using covariance matrix
        covmat = np.cov(new[bench + "_re"],new[ticker + "_re"])
        beta = covmat[0,1]/  np.sqrt(covmat[1,1]*covmat[0,0])
        betas.append(beta)
    betas = pd.DataFrame(betas)
    betas.index = ticker_list
    betas.columns=["Beta"]
    return betas, covmat

class get_robinhood:

	my_trader = Robinhood()

    # Placing buy orders (Robinhood.place_buy_order)
    # Placing sell order (Robinhood.place_sell_order)
    # Quote information (Robinhood.quote_data)
    # User portfolio data (Robinhood.portfolios)
    # User positions data (Robinhood.positions)
    # Examples:
    # stock_instrument = my_trader.instruments("GEVO")[0]
    # quote_info = my_trader.quote_data("GEVO")
    # buy_order = my_trader.place_buy_order(stock_instrument, 1)
    # sell_order = my_trader.place_sell_order(stock_instrument, 1)

	def get_universe(self):
        # must inclue Stock.xlsx in the dir
		self.universe=pd.read_excel('Stock.xlsx',sheet_name='USlist',header=0)
		return self.universe['Ticker']


	def get_historical(self,stock,interval='day',span='year',ifprint=False):
        
        
        #fetch historical data for stock

        #Note: valid interval/span configs
        #interval = 5minute | 10minute + span = day, week
        #interval = day + span = year
        #interval = week
        #TODO: NEEDS TESTS

        

		quote_info = self.my_trader.get_historical_quotes(stock,interval,span)['results']

		get_historical= DataFrame(quote_info[0]['historicals'])

		if (ifprint == True):

			get_historical.to_csv(stock + '.csv')


		return get_historical

	#Setup


	#Get stock information
	#Note: Sometimes more than one instrument may be returned for a given stock symbol

    #login
	def login(self,username,password):
		#username=str(input("Please input username"))
		#password = str(input("Please input password"))
		self.my_trader.login(username, password)

	def logout(self):
		self.my_trader.logout()


	def get_instrument(self,stock):


		profile = self.my_trader.instruments(stock)
		#profile = DataFrame(profile[0])
		profile = DataFrame(profile[0],index=[stock])


		return profile

	def get_fundamentals(self,stock):

		fundamentals = self.my_trader.get_fundamentals(stock)
		fundamentals = DataFrame(fundamentals,index=[stock])
		return fundamentals


	def get_stock_data(self,stock):

		quote = self.my_trader.quote_data(stock)

		quote = DataFrame(quote,index=[stock])

		return quote	


	def get_current_price(self,stock):

		quote = self.my_trader.quote_data(stock)

		quote = DataFrame(quote,index=[stock])

		return DataFrame(quote['adjusted_previous_close'])

	def order_history(self):

		orders = self.my_trader.order_history()
		orders = DataFrame(orders['results']).T
		

		return orders

	def positions_symbol(self):
		data = self.my_trader.positions()
		data = DataFrame(data['results'])
		data = data['instrument']
		out=list()
		
		for i in data:

			out.append(self.my_trader.get_url(i)['symbol'])

		return out

	def istradeable(self,stock):
		profile = self.my_trader.instruments(stock)
   
		if(profile == []):
			return Series(False,[str(stock)])

		profile_temp = DataFrame(profile[0],index=[stock])
		

		if (profile_temp['tradeable'][0]!= False | profile_temp['tradeable'][0] != True):
			i = i +1
			print "Connection may fail ", i

			return Series(False,[str(stock)])

		return profile_temp['tradeable']

	def place_buy(self, ticker,num):
	    for i in self.my_trader.instruments(ticker):
	        if i["symbol"]==ticker:
	            print ("Ticker found in instruments")
	            stock_inst = i
	        if self.my_trader.place_buy_order(stock_inst,num) == "<Response [201]>":
	            print "Trade Success!: " + stock_inst
	        else:
	            print "Trade Faile: " + stock_inst
	        time.sleep(10)
	def place_sell(self, ticker,num):
	    for i in self.my_trader.instruments(ticker):
	        if i["symbol"]==ticker:
	            print ("Ticker found in instruments")
	            stock_inst = i
	        if self.my_trader.place_sell_order(stock_inst,num) == "<Response [201]>":
	            print "Trade Success!: " + stock_inst
	        else:
	            print "Trade Faile: " + stock_inst
	        time.sleep(10)

	def get_my_positions(self):   
	    my_positions=[]
	    position_quantity = []
	    for i in self.my_trader.positions()["results"]:
	        if float(i["quantity"])>0:
	            position_quantity.append(float(i["quantity"]))
	            ticker = self.my_trader.get_url(i["instrument"])
	            my_positions.append(ticker["symbol"])
	            print ticker["symbol"] + " "+ str(i["quantity"])
	    return my_positions, position_quantity
	def get_buying_power(self):
	    buy = self.my_trader.get_account()["buying_power"]
	    print str(buy)
	    return float(buy)

	def get_my_position_beta(self):
	    stocks, quantity =self.get_my_positions()
	    quantity = pd.DataFrame(quantity,index = stocks,columns=["Quantity"])
	    betas = beta(stocks)
	    betas = pd.DataFrame(betas[0])
	    data = pd.concat([betas,quantity],axis=1)
	    data = data.fillna(1)
	    sum_beta=np.dot(data.Beta,data.Quantity)
	    print sum_beta
	    print data
	    return sum_beta,data


	#def get_my_position_chart (TODO)






	def place_buy_lumpsum_checkdup(self, ticker_list, quantity_list ):
		my_positions = self.get_my_positions()[0]
		for t, q in zip(ticker_list, quantity_list):
			if t in my_positions:
				self.place_buy(t,q)

	def place_buy_lumpsum_nocheck(self, ticker_list, quantity_list ):
		my_positions = self.get_my_positions()[0]
		for t, q in zip(ticker_list, quantity_list):
				self.place_buy(t,q)

