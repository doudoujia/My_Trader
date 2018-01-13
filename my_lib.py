
import time
import timeit
import talib as ta
import numpy as np
from Robinhood import Robinhood
from pandas import *
import xlrd
import  talib as ta
from datetime import datetime
from datetime import timedelta
from pandas_datareader import data as da
import pandas as pd
import numpy as np
from numpy import log, polyfit, sqrt, std, subtract
import statsmodels.tsa.stattools as ts
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import pprint

#********************************************************

# Class File

#********************************************************


#my robinhood file






#my_trader = Robinhood()





    

#get Finviz data

import requests as r
from bs4 import BeautifulSoup as bs
import numpy as np


class finviz:
    
    def get_finviz(self,symbol, data):
        try:
            base_url = 'http://finviz.com/quote.ashx?t={}'\
                .format(symbol.lower())
        
            html = r.get(base_url)
            soup = bs(html.content, "html.parser")
            main_div = soup.find('div', attrs = {'id':'screener-content'})
            pb =  soup.find(text = data)
            pb_ = pb.find_next(class_='snapshot-td2').text
            
            return pb_
        
        except:
            return np.NaN

    def get_finviz_sector(self,symbol):
        
        try:
            base_url = 'http://finviz.com/quote.ashx?t={}'\
            .format(symbol.lower())
            
            html = r.get(base_url)
            soup = bs(html.content, "html.parser")
            main_div = soup.find_all('td','fullview-links')
            sector = main_div[1].contents[0].text
            industry = main_div[1].contents[2].text
                
            return str(sector)
        except:
            return np.NaN

    def get_finviz_industry(self, symbol):
        try:
            base_url = 'http://finviz.com/quote.ashx?t={}'\
            .format(symbol.lower())
            
            html = r.get(base_url)
            soup = bs(html.content, "html.parser")
            main_div = soup.find_all('td','fullview-links')
            sector = main_div[1].contents[0].text
            industry = main_div[1].contents[2].text
                
            return str(industry)
        except:
            return np.NaN

    def get_marketcap(self,symbol):
        mkcap=self.get_finviz(symbol,"Market Cap")
        if type(mkcap) != unicode:
            return np.NaN
        else:
            if mkcap[-1]=="B":
                return float(mkcap[:-1])*1000000000
            elif mkcap[-1]=="M":
                return float(mkcap[:-1])*1000000
            else:
                return float(mkcap)


    def all_in_one(self, symbol):

        base_url = 'http://finviz.com/quote.ashx?t={}'\
            .format(symbol.lower())
            
        html = r.get(base_url)
        soup = bs(html.content, "html.parser")
        main_div = soup.find_all('td','fullview-links')
        sector = main_div[1].contents[0].text
        industry = main_div[1].contents[2].text

        main_div = soup.find('div', attrs = {'id':'screener-content'})
        pb =  soup.find(text = "Market Cap")
        mkt_cap = pb.find_next(class_='snapshot-td2').text
        earning_date = soup.find(text = "Earnings")
        earning_date = earning_date.find_next(class_='snapshot-td2').text

        if type(mkt_cap) != unicode:
            mkt_cap = np.NaN
        else:
            if mkt_cap[-1]=="B":
                mkt_cap = float(mkt_cap[:-1])*1000000000
            elif mkt_cap[-1]=="M":
                mkt_cap = float(mkt_cap[:-1])*1000000
            else:
                mkt_cap = float(mkt_cap)

        return str(industry), str(sector), mkt_cap,earning_date
    

finviz = finviz()
        

#yahoo finance 

import yahoo_finance
from yahoo_finance import Share
from pandas_datareader import data as pdr
import fix_yahoo_finance as yf
yf.pdr_override()

class yahoo_historicals:
    
        

    def get_historicals(self,stock, start,end):
    
        # download dataframe
        #start ="2017-01-01"
        #end="2017-04-30"
        data = pdr.get_data_yahoo(stock, start, end)

        return data

        
        



def conver_cap (mkcap):
    if mkcap[-1]=="B":
        return float(mkcap[:-1])*1000000000
    elif mkcap[-1]=="M":
        return float(mkcap[:-1])*1000000



def mean_reversion(stock,ival):

    result = []

    #***************************************

    # load price data

    #***************************************
    start ="2017-01-01"
    end=datetime.now()

    if ival == "day":
        st_price = da.DataReader(stock,"yahoo",start,end)
        st_price = st_price.dropna()
        usr_input = st_price["Adj Close"]

    elif ival == "minute":
        robinhood = get_robinhood()

    # use robinhood data for 10 minute interval
        st_price = robinhood.get_historical(stock,interval="10minute",span="week")
        usr_input = st_price.close_price.astype("float")
    else:
        raise "interval not support yet"



    #***************************************

    #Augmented Dickey Fuller test

    #***************************************


    

    cadf = ts.adfuller(usr_input)
    print 'Augmented Dickey Fuller test statistic =',cadf[0]
    print 'Augmented Dickey Fuller p-value =',cadf[1]
    print 'Augmented Dickey Fuller 1%, 5% and 10% test statistics =',cadf[4]

    #cadf[4]['1%'] get 1% statistic value
    print ('''
    p value should < 0.05

    ADF test statistic is larger than the benchmark in absolute value means we can reject 
    the null hypothesis that there is a unit root in the  time series, 
    and is therefore not mean reverting. We should look for a smaller value than benchmark to 
    keep the null hypothesis to confirm mean-reverting

    ''')
    


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

    if round(poly[0]*2.0,2)< 0.5:
        result.append("mean reverting")
    elif round(poly[0]*2.0,2)>0.5:
        result.append("trending")
    else:
        result.append("Geometric Brownian Motion ")

    #result.append(np.where(round(poly[0]*2.0,2)<0.5,"mean reverting","trending"))

    
    #H < 0.5  The time series is mean reverting 
    #H = 0.5  The time series is a Geometric Brownian Motion 
    #H > 0.5  The time series is trending
    



    #***************************************

    # Calculate Half life

    #***************************************


    #Run OLS regression on spread series and lagged version of itself

    df1 = usr_input

    lag = df1.shift(1)
    lag.iloc[0] = lag.iloc[1]
    ret = df1 - lag
    ret.iloc[0] = ret.iloc[1]
    lag2 = sm.add_constant(lag)
     
    model = sm.OLS(ret,lag2)
    res = model.fit()
     
     
    halflife = round(-np.log(2) / res.params[1],0)
     
    print  'Halflife = ', halflife

    result.append(halflife)

    if result[0] and result[1] == "mean reverting" and reverting[2]<30:

        result.append("Can trade")
    else:
        result.append("Can not trade")
    return result
