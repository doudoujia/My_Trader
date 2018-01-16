#import needed modules
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
from my_lib import *



def mean_reversion(stock,ival):

	result = []

	#***************************************

	# load price data

	#***************************************
	start ="2017-01-01"
	end=datetime.now()

	if ival == "day":
		st_price = da.DataReader(stock,"yahoo",start,end)

	elif ival == "minute":
		robinhood = get_robinhood()

	# use robinhood data for 10 minute interval
		st_price = robinhood.get_historical(stock,interval="10minute",span="week")

	else:
		raise "interval not support yet"



	#***************************************

	#Augmented Dickey Fuller test

	#***************************************


	usr_input = st_price.Close

	cadf = ts.adfuller(usr_input)
	print 'Augmented Dickey Fuller test statistic =',cadf[0]
	print 'Augmented Dickey Fuller p-value =',cadf[1]
	print 'Augmented Dickey Fuller 1%, 5% and 10% test statistics =',cadf[4]

	#cadf[4]['1%'] get 1% statistic value

	'''
	p value should < 0.05

	ADF test statistic is larger than the benchmark in absolute value means we can reject 
	the null hypothesis that there is a unit root in the  time series, 
	and is therefore not mean reverting. We should look for a smaller value than benchmark to 
	keep the null hypothesis to confirm mean-reverting

	'''


	if cadf[1] < 0.05 and (abs(cadf[0]) < abs(cadf[4]['1%']) or abs(cadf[0]) < abs(cadf[4]['10%']) or abs(cadf[0]) < abs(cadf[4]['5%'])):

		cadf_interpret = True
	else:
		cadf_interpret = False

	result.append(cadf_interpret)

	#***************************************

	# Calculate Hurst Exponent

	#***************************************


	"""Returns the Hurst Exponent of the time series vector ts"""
	# Create the range of lag values
	lags = range(2, 100)


	# Calculate the array of the variances of the lagged differences
	tau = [sqrt(np.std(np.subtract(usr_input[lag:], usr_input[:-lag]))) for lag in lags]
	 
	# Use a linear fit to estimate the Hurst Exponent
	lags = [log(i) for i in lags]
	tau = [log(i) for i in tau]
	poly = np.polyfit(lags,tau , 1)
	 
	# Return the Hurst exponent from the polyfit output


	# print the result
	print "Hurst Exponent =",round(poly[0]*2.0,2)
	result.append(round(poly[0]*2.0,2))

	
	#H < 0.5  The time series is mean reverting 
	#H = 0.5  The time series is a Geometric Brownian Motion 
	#H > 0.5  The time series is trending
	



	#***************************************

	# Calculate Half life

	#***************************************


	#Run OLS regression on spread series and lagged version of itself

	df1 = st_price.Close

	lag = df1.shift(1)
	lag.iloc[0] = lag.iloc[1]
	ret = df1 - lag
	ret.iloc[0] = ret.iloc[1]
	lag2 = sm.add_constant(lag)
	 
	model = sm.OLS(ret,lag2)
	res = model.fit()
	 
	 
	halflife = round(-np.log(2) / res.params[1],0)
	 
	print  'Halflife = ', halflife

	return result.append(halflife)


def moving_cross_backtest_day(stock, short_ma, long_ma,X = 10):
    #read in data from Yahoo Finance for the relevant ticker

    # You can change to other moving indicator as well
    stock['short_ma'] = np.round(stock['Close'].astype(float).rolling(window=short_ma).mean(),2)
    stock['long_ma'] = np.round(stock['Close'].astype(float).rolling(window=long_ma).mean(),2)

    #create column with moving average spread differential
    stock['short_ma-long_ma'] = stock['short_ma'] - stock['long_ma']

    #set desired number of points as threshold for spread difference and create column containing strategy 'Stance'
    
    stock['Stance'] = np.where(stock['short_ma-long_ma'] > X, 1, 0)
    stock['Stance'] = np.where(stock['short_ma-long_ma'] < X, -1, stock['Stance'])
    stock['Stance'].value_counts()

    #create columns containing daily market log returns and strategy daily log returns
    stock['Market Returns'] = np.log(stock['Close'].astype(float) / stock['Close'].astype(float).shift(1))
    stock['Strategy'] = stock['Market Returns'] * stock['Stance'].shift(1)

    #set strategy starting equity to 1 (i.e. 100%) and generate equity curve
    stock['Strategy Equity'] = stock['Strategy'].cumsum() + 1

    sharpe = annualised_sharpe(stock['Strategy'])

    cum_ret=stock['Strategy'].cumsum().iloc[-1]
    result = [cum_ret,sharpe]
    return result
 
#function to calculate Sharpe Ratio - Risk free rate element excluded for simplicity
def annualised_sharpe(returns, N=252):
    try:
        return np.sqrt(N) * (returns.mean() / returns.std())
    except ZeroDivisionError: 
        return 0




def moving_cross_backtest_10minute(ticker, short_ma, long_ma,X = 10):
    #read in data from Yahoo Finance for the relevant ticker
    
    ticker = ticker.upper()
    stock = robinhood.get_historical(ticker,interval="10minute",span="week")
    # You can change to other moving indicator as well
    stock['short_ma'] = np.round(stock['close_price'].astype(float).rolling(window=short_ma).mean(),2)
    stock['long_ma'] = np.round(stock['close_price'].astype(float).rolling(window=long_ma).mean(),2)

    #create column with moving average spread differential
    stock['short_ma-long_ma'] = stock['short_ma'] - stock['long_ma']

    #set desired number of points as threshold for spread difference and create column containing strategy 'Stance'
    
    stock['Stance'] = np.where(stock['short_ma-long_ma'] > X, 1, 0)
    stock['Stance'] = np.where(stock['short_ma-long_ma'] < X, -1, stock['Stance'])
    stock['Stance'].value_counts()

    #create columns containing daily market log returns and strategy daily log returns
    stock['Market Returns'] = np.log(stock['close_price'].astype(float) / stock['close_price'].astype(float).shift(1))
    stock['Strategy'] = stock['Market Returns'] * stock['Stance'].shift(1)

    #set strategy starting equity to 1 (i.e. 100%) and generate equity curve
    stock['Strategy Equity'] = stock['Strategy'].cumsum() + 1

    sharpe = annualised_sharpe(stock['Strategy'],9828)

    cum_ret=stock['Strategy'].cumsum().iloc[-1]
    result = [cum_ret,sharpe]
    return result

def moving_cross_backtest(ticker, period):
    
    #---------------------------------------------------------------
    period = period.lower()
    if period == "day":
        stock = da.DataReader(ticker,"yahoo","2017-01-01",datetime.now())
        try:
            
            reversion_test = mean_reversion(ticker,"day")
            short_ma = np.linspace(10,10+5*reversion_test[2],20,dtype=int)
            long_ma = np.linspace(60,60+5*reversion_test[2],20,dtype=int)
            results_cum_ret = np.zeros((len(short_ma),len(long_ma)))
            results_sharpe = np.zeros((len(short_ma),len(long_ma)))
        except:
            
            short_ma = np.linspace(10,10+5*20,20,dtype=int)
            long_ma = np.linspace(60,60+20,20,dtype=int)
            results_cum_ret = np.zeros((len(short_ma),len(long_ma)))
            results_sharpe = np.zeros((len(short_ma),len(long_ma)))
            raise "except used, probably cannot convert"
            exit()
        
        for i, shortma in enumerate(short_ma):
            for j, longma in enumerate(long_ma):
                results = moving_cross_backtest_day(stock,shortma,longma)
                results_cum_ret[i,j] = results[0]
                results_sharpe[i,j] = results[1]
        #plt.figure(figsize=(8,8))
        plt.pcolor(short_ma,long_ma,results_cum_ret)
        plt.colorbar()
        plt.show()

    elif period =="minute":
        try:
            
            reversion_test = mean_reversion(ticker,"minute")
            short_ma = np.linspace(10,10+5*reversion_test[2],20,dtype=int)
            long_ma = np.linspace(60,60+5*reversion_test[2],20,dtype=int)
            results_cum_ret = np.zeros((len(short_ma),len(long_ma)))
            results_sharpe = np.zeros((len(short_ma),len(long_ma)))
        except:
            
            short_ma = np.linspace(10,10+5*20,20,dtype=int)
            long_ma = np.linspace(60,60+5*20,20,dtype=int)
            results_cum_ret = np.zeros((len(short_ma),len(long_ma)))
            results_sharpe = np.zeros((len(short_ma),len(long_ma)))
            raise "except used, probably cannot convert"
            exit()
        short_ma = np.linspace(10,10+5*reversion_test[2],20,dtype=int)
        long_ma = np.linspace(60,60+5*reversion_test[2],20,dtype=int)
        results_cum_ret = np.zeros((len(short_ma),len(long_ma)))
        results_sharpe = np.zeros((len(short_ma),len(long_ma)))
        for i, shortma in enumerate(short_ma):
            for j, longma in enumerate(long_ma):
                results = moving_cross_backtest_10minute(stock,shortma,longma)
                results_cum_ret[i,j] = results[0]
                results_sharpe[i,j] = results[1]
        #plt.figure(figsize=(8,8))
        plt.pcolor(short_ma,long_ma,results_cum_ret)
        plt.colorbar()
        plt.show()


def plot_ticker(ticker, fast_win,slow_win):
    stock = da.DataReader(ticker,"yahoo","2017-01-01",datetime.now())
    stock["mv_fast"]=stock["Adj Close"].rolling(20).mean()
    stock["mv_slow"]=stock["Adj Close"].rolling(40).mean()
    plt.title(ticker)
    #my_plt = plt.plot(stock[["Adj Close","mv_fast","mv_slow"]])
    stock[["Adj Close","mv_fast","mv_slow"]].plot(figsize=(18,8))
    plt.legend(["Adj Close","mv_fast","mv_slow"])
    plt.show()


def plot_position(tickers, quantity):
    temp = da.DataReader(tickers[0],"yahoo",datetime.now()-timedelta(days=90),datetime.now())
    data = pd.DataFrame(index=temp.index)
    temp = temp.rename(columns={"Adj Close":str(tickers[0]) + "_Close"})
    temp = temp.rename(columns={"High":str(tickers[0]) + "_High"})
    temp = temp.rename(columns={"Low":str(tickers[0]) + "_Low"})
    data = pd.concat([data,temp[[str(tickers[0]) + "_Close",str(tickers[0]) + "_High",str(tickers[0]) + "_Low"]]], axis=1)
    for i in tickers[1:]:
        temp = da.DataReader(i,"yahoo",datetime.now()-timedelta(days=90),datetime.now())
        temp = temp.rename(columns={"Adj Close":str(i) + "_Close"})
        temp = temp.rename(columns={"High":str(i) + "_High"})
        temp = temp.rename(columns={"Low":str(i) + "_Low"})
        data = pd.concat([data,temp[[str(i) + "_Close",str(i) + "_High",str(i) + "_Low"]]], axis=1)
    data_weighted = pd.DataFrame(index = data.index)
    for i, j in zip(data.columns,range(len(data)*3)):
        j = j % 3
        data_weighted = pd.concat([data_weighted,data[i] * quantity[j]],axis=1)
    data_weighted["Sum_Close"] = data_weighted.filter(regex="Close").sum(axis=1)
    data_weighted["Sum_High"] = data_weighted.filter(regex="High").sum(axis=1)
    data_weighted["Sum_Low"] = data_weighted.filter(regex="Low").sum(axis=1)
    data_weighted["Sum_Close_MA_F"] = data_weighted.Sum_Close.rolling(5).mean()
    data_weighted["Sum_Close_MA_S"] = data_weighted.Sum_Close.rolling(20).mean()

    data_weighted["STOCH_slowk"], data_weighted["STOCH_slowd"] = ta.STOCHF(data_weighted["Sum_High"].values, data_weighted["Sum_Low"].values, data_weighted["Sum_Close"].values, fastk_period=5, fastd_period=3, fastd_matype=0)
    plt.figure(1,figsize = (18,18))
    sub = plt.subplot(211)
    plt.title("Position")
    data_weighted.Sum_Close.plot()
    data_weighted.Sum_Close_MA_F.plot()
    data_weighted.Sum_Close_MA_S.plot()
    plt.legend()
    plt.subplot(212,sharex=sub)
    plt.title("STOCH")
    data_weighted.STOCH_slowd.plot()
    data_weighted.STOCH_slowk.plot()

    plt.show()
	
