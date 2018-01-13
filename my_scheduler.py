from my_lib import *
import time
import timeit
import talib as ta
import numpy as np
from Robinhood import Robinhood
import pandas as pd
import xlrd
from datetime import datetime
from pandas_datareader import data as da
import schedule

def job():
	


	tradeable = pd.read_csv("file/cantrade.csv")
	tradeable = tradeable.dropna()

	error = []


	yahoo = yahoo_historicals()
	start ="2017-10-1"
	end=datetime.now()
	price=pd.DataFrame()




	for i in list(tradeable.Ticker):
	    trial = 0
	    while trial <3:
	        try:
	            temp = da.DataReader(i,"yahoo",start,end)
	            index= pd.MultiIndex.from_product([[i],temp.index])
	            temp=pd.DataFrame(data=temp.values,index=index,columns=temp.columns)
	            price = price.append(temp)

	            print "Finished", i 
	            #time.sleep(5)
	            trial=3

	        except:
	            print "error occorded in getting yahool historicals for ", i
	            trial +=1
	            if trial == 3:
	                error.append([i,'get_yahoo_historicals'])
	# get rid of the multiindex 
	price.to_csv("file/price_update.csv")



	price = pd.read_csv(file/"price_update.csv")


	price.Close = price["Adj Close"]
	price = price.rename(columns={'Unnamed: 0':'Ticker','Unnamed: 1':"TimeStamp"})
	price["Return"]= price.Close.diff(1)/price.Close

	'''
	# make sure DataFrames are the same length

	price_date = pd.DataFrame()

	min_date = max(price.loc[price.Ticker==i].TimeStamp.iloc[0] for i in price.Ticker)
	max_date = min(price.loc[price.Ticker==i].TimeStamp.iloc[-1] for i in price.Ticker)
	print "2"
	for i in price.Ticker:
	    price_date = price_date.append(price.loc[price.Ticker==i][(price.loc[price.Ticker==i].TimeStamp>= min_date) & (price.loc[price.Ticker==i].TimeStamp <= max_date)] )

	price = price_date

	print "done"

	'''


	industry_sector_earnings = pd.read_csv("file/my_universe_industry_sector_marketcap_earnings.csv")
	#earnings = pd.read_csv("my_universe_earnings.csv")

	industry_sector_earnings = industry_sector_earnings.dropna()  
	    


	for i in list(set(price.Ticker)):
	    
	    #print price .loc[price.Ticker==i]

	    #price.groupby('Ticker').get_group(list(set(price.Ticker))[i])
	    #price.loc[price.Ticker==i,"ADX"]= ta.ADX(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, timeperiod=14)
	    price.loc[price.Ticker==i,"ADXR"]= ta.ADXR(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, timeperiod=14)
	    price.loc[price.Ticker==i,"APO"]= ta.APO(price.loc[price.Ticker==i].Close.values, fastperiod=12, slowperiod=26, matype=0)
	    price.loc[price.Ticker==i,"AROONOSC"]= ta.AROONOSC(price.loc[price.Ticker==i].High.values,price.loc[price.Ticker==i].Close.values, timeperiod=14)
	    price.loc[price.Ticker==i,"CCI"]= ta.CCI(price.loc[price.Ticker==i].High.values,price.loc[price.Ticker==i].Low.values,price.loc[price.Ticker==i].Close.values, timeperiod=14)
	    price.loc[price.Ticker==i,"MFI"]= ta.MFI(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, price.loc[price.Ticker==i].loc[price.Ticker==i].Volume.values.astype(float),timeperiod=14)
	    price.loc[price.Ticker==i,"MACD"], price.loc[price.Ticker==i,"MACD_signal"], price.loc[price.Ticker==i,"MACD_hist"] = ta.MACD(price.loc[price.Ticker==i].Close.values, fastperiod=12, slowperiod=26, signalperiod=9)
	    price.loc[price.Ticker==i,"ROCP"]= ta.ROCP(price.loc[price.Ticker==i].Close.values, timeperiod=10)
	    #price.loc[price.Ticker==i,"ROCR100"]= ta.ROCR100(price.loc[price.Ticker==i].Close.values, timeperiod=10)
	    price.loc[price.Ticker==i,"RSI"]= ta.RSI(price.loc[price.Ticker==i].Close.values, timeperiod=14)

	    print "\nDone:", i



	final_update = pd.DataFrame()

	for i in list(set(price.Ticker)):

	    final_update = final_update.append(price.loc[price.Ticker==i].iloc[-1])


	final_update["Industry"] = np.NaN
	final_update["Sector"] = np.NaN
	final_update["Earnings_date"] = np.NaN
	final_update["Market_cap"] = np.NaN
	final_update["Industry_weight"] = np.NaN

	for i in list(set(final_update.Ticker)):
	    try:
	        final_update.loc[final_update.Ticker==i,"Industry"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Industry"].values[0]
	    except:
	        
	        print "nan occorded"

	for i in list(set(final_update.Ticker)):    
	    try:
	        final_update.loc[final_update.Ticker==i,"Sector"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Sector"].values[0]
	    except:
	        
	        print "nan occorded"
	for i in list(set(final_update.Ticker)):    
	    try:
	        final_update.loc[final_update.Ticker==i,"Earnings_date"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Earnings_date"].values[0] 
	    except:
	        
	        print "nan occorded"

	for i in list(set(final_update.Ticker)):    
	    try:
	        final_update.loc[final_update.Ticker==i,"Market_cap"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Market_cap"].values[0] 
	    except:
	        
	        print "nan occorded"



	#final_update.to_csv("final"+str(price.loc[price.Ticker==i][-1]["Date"])+".csv")


	#get industrial makcap_weight

	for ind in set(final_update.Industry):
	    for tic in set(final_update.loc[final_update.Industry==ind].Ticker):
	        final_update.loc[final_update.Ticker==tic,'Industry_weight']=final_update.loc[final_update.Ticker==tic,"Market_cap"] / final_update.loc[final_update.Industry==ind,"Market_cap"].sum()


	#final_update = final_update[['Ticker','TimeStamp', 'Open', 'High', 'Low', 'Close', 'Volume',
	#        'Return','ADXR','AROONOSC','APO','CCI','MACD', 'MACD_hist',
	#       'MACD_signal','MFI','ROCP','RSI','Industry','Sector']]
	final_update = final_update[['Ticker','TimeStamp', 'Open', 'High', 'Low', 'Close', 'Volume',
	        'Return','ADXR','AROONOSC','APO','CCI','MACD', 'MACD_hist',
	       'MACD_signal','MFI','ROCP','RSI','Industry','Sector','Market_cap','Industry_weight','Earnings_date']]

	final_update =final_update.set_index("Ticker")

	#final_update= final_update.dropna()




	# Technical points rule

	final_update["Technical_points"]=0
	for i in final_update.index:
	    if final_update.loc[i].ADXR >= final_update.loc[final_update.Sector==final_update.loc[i].Sector].max().ADXR:
	        final_update.loc[i,'Technical_points'] += 1
	    if final_update.loc[i].APO >0:
	        final_update.loc[i,'Technical_points'] += 1
	    if final_update.loc[i].AROONOSC >= final_update.loc[final_update.Sector==final_update.loc[i].Sector].max().AROONOSC:
	        final_update.loc[i,'Technical_points'] += 1
	    if final_update.loc[i].CCI <-100:
	        final_update.loc[i,'Technical_points'] += 1
	    if final_update.loc[i].MACD > final_update.loc[i].MACD_signal:
	        final_update.loc[i,'Technical_points'] += 1
	    if final_update.loc[i].MFI <20:
	        final_update.loc[i,'Technical_points'] += 1
	    if final_update.loc[i].ROCP >0:
	        final_update.loc[i,'Technical_points'] += 1

	    print "Technical_points done: ", i
	final_update= final_update.dropna()

	final_update.to_csv("file/final_update.csv")
	#***************************************

	# get result

	#***************************************

	result = pd.DataFrame()
	for i in set(final_update.Sector):
	    print i
	    print final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-1].name
	    result = result.append(final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-1])

	result.to_csv("file/Trade_suggestion" + str(datetime.now())[0:10]+".csv")











schedule.every().day.at("05:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)