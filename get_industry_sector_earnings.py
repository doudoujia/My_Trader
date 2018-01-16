# first, get can_trade universe


from my_lib import *

def update_fundamentals():
	error=[]

	test=get_robinhood()
	#test.login()
	universe = test.get_universe()

	stock = list();



	print "checking robinhood cantrade\n"
	tradeable = universe.loc[list(test.istradeable(str(universe.iloc[i]))[0] for i in range(len(universe.index)))]

	tradeable = DataFrame(tradeable,columns=['Ticker'])


	#get industry, sector and market cap

	tradeable.to_csv('file/cantrade.csv')


	print "cantrade done!\n"


	start = timeit.default_timer()
	tradeable = pd.read_csv("file/cantrade.csv")

	tradeable['Industry']=np.NaN
	tradeable['Sector']=np.NaN
	tradeable['Market_cap']=np.NaN
	tradeable['Earnings_date']=np.NaN

	for i in range(len(tradeable.index)):
		try:
		    tradeable['Industry'].iloc[i],tradeable['Sector'].iloc[i],tradeable['Market_cap'].iloc[i],tradeable['Earnings_date'].iloc[i]=finviz.all_in_one(tradeable['Ticker'].iloc[i])
		    print "get done! ", tradeable['Ticker'].iloc[i]
		    if i % 8 == 0 and i != 0:
		        time.sleep(20)
		except:
			print "get error"
			error.append([tradeable['Ticker'].iloc[i],'get_S_I_M_E'])

	error = pd.DataFrame(error)

	tradeable.to_csv("file/my_universe_industry_sector_marketcap_earnings.csv")
	error.to_csv("file/error.csv")

	stop = timeit.default_timer()

	runtime = stop - start
	print  runtime