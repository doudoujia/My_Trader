from my_lib import *
from pandas_datareader import data as da
import pandas as pd


def moving_cross_backtest_day(stock, short_ma, long_ma):
    #read in data from Yahoo Finance for the relevant ticker

    # You can change to other moving indicator as well
    stock['short_ma'] = np.round(stock['Close'].astype(float).rolling(window=short_ma).mean(),2)
    stock['long_ma'] = np.round(stock['Close'].astype(float).rolling(window=long_ma).mean(),2)

    #create column with moving average spread differential
    stock['short_ma-long_ma'] = stock['short_ma'] - stock['long_ma']

    #set desired number of points as threshold for spread difference and create column containing strategy 'Stance'
    X = 10
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
    return np.sqrt(N) * (returns.mean() / returns.std())





def moving_cross_backtest_10minute(ticker, short_ma, long_ma):
    #read in data from Yahoo Finance for the relevant ticker
    
    ticker = ticker.upper()
    stock = robinhood.get_historical(ticker,interval="10minute",span="week")
    # You can change to other moving indicator as well
    stock['short_ma'] = np.round(stock['close_price'].astype(float).rolling(window=short_ma).mean(),2)
    stock['long_ma'] = np.round(stock['close_price'].astype(float).rolling(window=long_ma).mean(),2)

    #create column with moving average spread differential
    stock['short_ma-long_ma'] = stock['short_ma'] - stock['long_ma']

    #set desired number of points as threshold for spread difference and create column containing strategy 'Stance'
    X = 10
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
        reversion_test = mean_reversion(ticker,"day")
    
        short_ma = np.linspace(10,10+5*reversion_test[2],10,dtype=int)
        long_ma = np.linspace(60,60+5*reversion_test[2],10,dtype=int)
        results_cum_ret = np.zeros((len(short_ma),len(long_ma)))
        results_sharpe = np.zeros((len(short_ma),len(long_ma)))
        for i, shortma in enumerate(short_ma):
            for j, longma in enumerate(long_ma):
                results = moving_cross_backtest_day(stock,shortma,longma)
                results_cum_ret[i,j] = results[0]
                results_sharpe[i,j] = results[1]
        plt.figure(figsize=(8,8))
        plt.pcolor(short_ma,long_ma,results_cum_ret)
        plt.colorbar()
        plt.show()

    elif period =="10minute":
        reversion_test = mean_reversion(ticker,"minute")
        short_ma = np.linspace(10,10+5*reversion_test[2],10,dtype=int)
        long_ma = np.linspace(60,60+5*reversion_test[2],10,dtype=int)
        results_cum_ret = np.zeros((len(short_ma),len(long_ma)))
        results_sharpe = np.zeros((len(short_ma),len(long_ma)))
        for i, shortma in enumerate(short_ma):
            for j, longma in enumerate(long_ma):
                results = moving_cross_backtest_10minute(stock,shortma,longma)
                results_cum_ret[i,j] = results[0]
                results_sharpe[i,j] = results[1]
        plt.figure(figsize=(8,8))
        plt.pcolor(short_ma,long_ma,results_cum_ret)
        plt.colorbar()
        plt.show()


    
     
 
    