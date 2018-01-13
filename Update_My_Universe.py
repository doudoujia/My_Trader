import my_lib
import pandas 
import time
import timeit
import talib as ta
#********************************************************

# My universe update


#********************************************************

#get trading universe

error = list()



'''

start_whole = timeit.default_timer()

test=get_robinhood()
#test.login()
universe = test.get_universe()

stock = list();





tradeable = universe.loc[list(test.istradeable(str(universe.iloc[i]))[0] for i in range(len(universe.index)))]

tradeable = DataFrame(tradeable,columns=['Ticker'])

#get sector

tradeable.to_csv('cantrade.csv')


tradeable = pd.read_csv('cantrade.csv')


start = timeit.default_timer()

tradeable['Sector'] = np.NaN

for i in range(len(tradeable.index)):
	try:
	    tradeable['Sector'].iloc[i]=finviz.get_finviz_sector(tradeable['Ticker'].iloc[i])
	    if i % 8 == 0 :
	        time.sleep(20)
	except:
		tradeable['Sector'].iloc[i]='get_error'
		error.append([tradeable['Ticker'].iloc[i],'get_sector'])


tradeable.to_csv("my_universe.csv")

stop = timeit.default_timer()
#tradeable['Sector'] = pd.Series( finviz.get_finviz_sector(tradeable['Ticker'][i]) for i in range(10) )

runtime = stop - start

print "Get sector runtime: ",runtime



tradeable = pd.read_csv('my_universe.csv')
#get industry

start = timeit.default_timer()

tradeable['Industry']=np.NaN

for i in range(len(tradeable.index)):
	try:
	    tradeable['Industry'].iloc[i]=finviz.get_finviz_industry(tradeable['Ticker'].iloc[i])
	    if i % 8 == 0 :
	        time.sleep(20)
	except:
		tradeable['Industry'].iloc[i]='get_error'
		error = error.append([tradeable['Ticker'][i],'get_sector'])


tradeable.to_csv("my_universe_industry.csv")

stop = timeit.default_timer()
#tradeable['Sector'] = pd.Series( finviz.get_finviz_sector(tradeable['Ticker'][i]) for i in range(10) )

runtime = stop - start

print "Get industry runtime: ", runtime


#dividing into different industries, using multiindexing

tradeable["Earnings_Date"]=np.NaN
for i in list(set(tradeable.Industry)):
    for j in tradeable.loc[tradeable.Industry==i]["Ticker"]:
        try:
            tradeable.loc[tradeable.loc[tradeable.Ticker==j].index.values,"Earnings_Date"]=finviz.get_finviz(j,"Earnings")
            i
        except:
            tradeable.loc[tradeable.loc[tradeable.Ticker==j].index.values,"Earnings_Date"]="try later"
            error.append([j,'Earnings_Date'])
    
        if list(set(tradeable.Industry)).index(i) % 8 == 0 :
            time.sleep(15)
            
tradeable.to_csv('my_universe_earnings.csv')

stop = timeit.default_timer()

runtime = stop - start

print "Get Earnings_Date runtime: ", runtime

#get market cap

start = timeit.default_timer()

tradeable['market_cap'] = np.NaN

for i in range(len(tradeable.index)):
    try:
        tradeable['market_cap'].iloc[i]=finviz.get_marketcap(tradeable['Ticker'].iloc[i])
        if i % 8 == 0 :
            time.sleep(20)
    except:
        tradeable['market_cap'].iloc[i]='get_error'
        error.append([tradeable['Ticker'].iloc[i],'get_market_cap'])


tradeable.to_csv("my_universe.csv")

stop = timeit.default_timer()



#***************************************

# Add price data and Technical Analysis indicator

#***************************************

#need to change this line after testing
#tradeable=pd.read_excel('Stock.xlsx',sheet_name='USlist',header=0)




google = google_historicals()
yahoo = yahoo_historicals()
start ="2017-01-01"
end="2017-04-30"
price=DataFrame()


for i in list(tradeable.Ticker):
    end = 0
    while end <20:
        try:
            temp=google.get_historicals(i)
            if temp.empty:
                temp = yahoo.get_historicals(i,start,end)
            index= pd.MultiIndex.from_product([[i],temp.index])
            temp=DataFrame(data=temp.values,index=index,columns=temp.columns)
            price = price.append(temp)
            print "Finished", i 
            #time.sleep(5)
            end=20
        except:
            print "error occorded in getting google historicals for ", i
            if end == 20:
                error.append([i,'get_google_historicals'])
        
    


price.to_csv('pricedata.csv')







analysis = pd.read_csv('pricedata.csv')
analysis = analysis.rename(columns={'Unnamed: 0':'Ticker','Unnamed: 1':"TimeStamp"})
analysis["Return"]= analysis.Close.diff(1)/analysis.Close



for i in list(set(analysis.Ticker)):
    
    #print analysis .loc[analysis.Ticker==i]

    #analysis.groupby('Ticker').get_group(list(set(analysis.Ticker))[i])
    analysis.loc[analysis.Ticker==i,"ADX"]= ta.ADX(analysis.loc[analysis.Ticker==i].High.values, analysis.loc[analysis.Ticker==i]\
    	.Low.values, analysis.loc[analysis.Ticker==i].Close.values, timeperiod=14)
    analysis.loc[analysis.Ticker==i,"ADXR"]= ta.ADXR(analysis.loc[analysis.Ticker==i].High.values, analysis.loc[analysis.Ticker==i].Low.values, analysis.loc[analysis.Ticker==i].Close.values, timeperiod=14)
    analysis.loc[analysis.Ticker==i,"APO"]= ta.APO(analysis.loc[analysis.Ticker==i].Close.values, fastperiod=12, slowperiod=26, matype=0)
    analysis.loc[analysis.Ticker==i,"AROONOSC"]= ta.AROONOSC(analysis.loc[analysis.Ticker==i].High.values,analysis.loc[analysis.Ticker==i].Close.values, timeperiod=14)
    analysis.loc[analysis.Ticker==i,"CCI"]= ta.CCI(analysis.loc[analysis.Ticker==i].High.values,analysis.loc[analysis.Ticker==i].Low.values,analysis.loc[analysis.Ticker==i].Close.values, timeperiod=14)
    analysis.loc[analysis.Ticker==i,"MFI"]= ta.MFI(analysis.loc[analysis.Ticker==i].High.values, analysis.loc[analysis.Ticker==i].Low.values, analysis.loc[analysis.Ticker==i].Close.values, analysis.loc[analysis.Ticker==i].loc[analysis.Ticker==i].Volume.values.astype(float),timeperiod=14)
    analysis.loc[analysis.Ticker==i,"MACD"], analysis.loc[analysis.Ticker==i,"MACD_signal"], analysis.loc[analysis.Ticker==i,"MACD_hist"] = ta.MACD(analysis.loc[analysis.Ticker==i].Close.values, fastperiod=12, slowperiod=26, signalperiod=9)
    analysis.loc[analysis.Ticker==i,"ROCP"]= ta.ROCP(analysis.loc[analysis.Ticker==i].Close.values, timeperiod=10)
    analysis.loc[analysis.Ticker==i,"ROCR100"]= ta.ROCR100(analysis.loc[analysis.Ticker==i].Close.values, timeperiod=10)
    analysis.loc[analysis.Ticker==i,"RSI"]= ta.RSI(analysis.loc[analysis.Ticker==i].Close.values, timeperiod=14)
    
analysis.to_csv("Technical_analysis.csv")


#***************************************

# import Fundamental data to price multiindex dataframe

#***************************************


analysis= pd.read_csv("Technical_analysis.csv")

industry = pd.read_csv("my_universe_industry.csv")
analysis['Industry']=np.NaN

for i in list(set(industry.Industry)):
    try:
        i = str(i)
        select = industry.loc[industry.Industry == i].Ticker
        analysis.loc[analysis.Ticker.isin(select),'Industry'] = i
    except:
        print "error occored", i
        error.append([i,'import Industry'])
        
        

analysis['Sector']=np.NaN

for i in list(set(industry.Sector)):
    try:
        i = str(i)
        select = industry.loc[industry.Sector == i].Ticker
        analysis.loc[analysis.Ticker.isin(select),'Sector'] = i
    except:
        print "error occored", i
        error.append([i,'import Sector'])

analysis.to_csv('industry_sector.csv')







#***************************************

# Transform the timeseries data to newest date data

#***************************************

analysis=pd.read_csv('industry_sector.csv')


newest_non_timeseries = pd.DataFrame()


for i in set(analysis.Ticker):
    newest_non_timeseries=newest_non_timeseries.append(analysis.loc[analysis.Ticker==i].iloc[-1])

newest_non_timeseries.to_csv("newest_non_timeseries.csv")


'''

#***************************************

# get market cap

#***************************************


analysis = pd.read_csv("newest_non_timeseries.csv")


analysis['market_cap'] = np.NaN

for i in range(len(analysis.index)):
    try:
        analysis['market_cap'].iloc[i]=finviz.get_marketcap(analysis['Ticker'].iloc[i])
        if i % 8 == 0 :
            time.sleep(20)
        print "Success: ", analysis['Ticker'].iloc[i]
    except:
        print "Error: ", analysis['Ticker'].iloc[i]
        analysis['market_cap'].iloc[i]='get_error'
        error.append([analysis['Ticker'].iloc[i],'get_market_cap'])


analysis.to_csv("market_cap_added.csv")


# change market_cap datatype

analysis = analysis.drop(analysis.loc[analysis["market_cap"]=="get_error"].index,0)

analysis["market_cap"]=analysis["market_cap"].astype(float)


analysis.to_csv("final.csv")




error = DataFrame(error).to_csv("error.csv")
stop_whole = timeit.default_timer()
print "The whole program time is ", stop_whole - start_whole






