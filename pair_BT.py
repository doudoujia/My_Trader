def pair_trade(stock1, stock2,initial,method = "day",window = 30,data_len = 210, continuous = False):    
    robinhood = get_robinhood()
    # stock1 = "VIXY"
    # stock2 = "SPY"
    if method == "day":
        price1 = get_price_data([stock1],method="day",start_date=datetime.now()-timedelta(days=data_len),end_date=datetime.now()-timedelta(days=0))
        price2 = get_price_data([stock2],method="day",start_date=datetime.now()-timedelta(days=data_len),end_date=datetime.now()-timedelta(days=0))
    elif method == "minute":
        price1 = get_price_data([stock1],method = "robinhood")
        price2 = get_price_data([stock2],method = "robinhood")
    price1 = price1.set_index("TimeStamp")
    price2 = price2.set_index("TimeStamp")
    price1 = price1.rename(columns={"Close":stock1+"_close"})
    price2 = price2.rename(columns={"Close":stock2+"_close"})



    price_table = pd.concat([price1[stock1+"_close"],price2[stock2+"_close"]],axis = 1)
    price_table = price_table.fillna(price_table.shift(1))
    price_table[stock1+"_close"] = price_table[stock1+"_close"].astype(float)
    price_table[stock2+"_close"] = price_table[stock2+"_close"].astype(float)
    price_table[stock1+"_log_ret"] = log(price_table[stock1+"_close"] / price_table[stock1+"_close"].shift(1))
    price_table[stock2+"_log_ret"] = log(price_table[stock2+"_close"] / price_table[stock2+"_close"].shift(1))

    #price_table=price_table.fillna(1)

    price_table[stock1+"_log_ret_mv"] = price_table[stock1+"_log_ret"].rolling(window).mean()
    price_table[stock2+"_log_ret_mv"] =price_table[stock2+"_log_ret"].rolling(window).mean()
    price_table["relative"]=price_table[stock1+"_log_ret"]/price_table[stock2+"_log_ret"]
    price_table["relative_mv"] = price_table["relative"].rolling(window).mean()

    price_table.relative.loc[price_table.relative==-np.inf]=price_table.relative.shift(1)

    #price_table["relative_mv"]=price_table[stock1+"_log_ret_mv"]/price_table[stock2+"_log_ret_mv"]
    price_table["z_score"] =( price_table["relative"]-price_table["relative_mv"])/price_table.relative.std()
    price_table["trade"]=0
    price_table["trade_signal"]=np.NaN
    price_table["slope"]=0
    for i in range(window-1,len(price_table)):
        price_table["slope"].iloc[i] = stats.linregress(price_table[stock1+"_log_ret"]\
                                                        .iloc[i-(window-1):i],price_table[stock2+"_log_ret"].iloc[i-(window-1):i])[0]
    price_table["buy_line"] = np.NaN

    print ("Log return done, 10%")

    for i in range(window-1,len(price_table)):
        if price_table.slope.iloc[i]>0.5:
            price_table["buy_line"].iloc[i] = -1.25
        elif price_table.slope.iloc[i]>0.75:
            price_table["buy_line"].iloc[i]= -1.75
        elif price_table.slope.iloc[i]<-0.5:
            price_table["buy_line"].iloc[i] -2.25
        elif price_table.slope.iloc[i]<-0.75:
            price_table["buy_line"].iloc[i]= -2.75
        else:
            price_table["buy_line"].iloc[i] = -2
     
    price_table["sell_line"] = np.NaN
    for i in range(window-1,len(price_table)):
        if price_table.slope.iloc[i]>0.5:
            price_table["sell_line"].iloc[i] = 1.25
        elif price_table.slope.iloc[i]>0.75:
            price_table["sell_line"].iloc[i] = 1.75
        elif price_table.slope.iloc[i]<-0.5:
            price_table["sell_line"].iloc[i] = 2.25
        elif price_table.slope.iloc[i]<-0.75:
            price_table["sell_line"].iloc[i] = 2.75
        else:
            price_table["sell_line"].iloc[i] = 2  
    print ("Signal Line done, 30%")           
    #no short sell

    price_table["relative_mv"] = abs(price_table["relative_mv"])

            
    #price_table["cost_per_trade"] =abs( price_table[stock1+"_close"]+price_table[stock2+"_close"]*price_table["relative_mv"])
    price_table[stock1+"_suggest_shares"] = np.ceil((initial/(1+price_table["relative_mv"])/price_table[stock1+"_close"]))
    price_table[stock2+"_suggest_shares"] = np.ceil((initial/(1+price_table["relative_mv"])*price_table["relative_mv"]/price_table[stock2+"_close"]))


    #set live trade signal and backtest 
    price_table[stock1+"_shares"] = 0 
    price_table[stock2+"_shares"] = 0
    for i in range(window-1,len(price_table)):
        if price_table.z_score.iloc[i] < price_table.buy_line.iloc[i]:
            price_table["trade"].iloc[i] = 1
            price_table["trade_signal"].iloc[i] = 1
            price_table[stock1+"_shares"].iloc[i] = price_table[stock1+"_suggest_shares"].iloc[i]
            price_table[stock2+"_shares"].iloc[i] = price_table[stock2+"_suggest_shares"].iloc[i]
        elif price_table.z_score.iloc[i] > price_table.sell_line.iloc[i]:
            price_table["trade"].iloc[i] = 0
            price_table["trade_signal"].iloc[i] = 0
            price_table[stock1+"_shares"].iloc[i] = 0 
            price_table[stock2+"_shares"].iloc[i] = 0
        else:
            price_table["trade"].iloc[i] = price_table.trade.iloc[i-1]
            price_table[stock1+"_shares"].iloc[i] = price_table[stock1+"_shares"].iloc[i-1]
            price_table[stock2+"_shares"].iloc[i] = price_table[stock2+"_shares"].iloc[i-1]
    print ("Trade singal done, 60%") 
    if not continuous:
        price_table[stock1+"_value"] = price_table[stock1+"_shares"].shift(1)*price_table[stock1+"_close"].shift(1)
        price_table[stock2+"_value"] = price_table[stock2+"_shares"].shift(1)*price_table[stock2+"_close"].shift(1)
        price_table["p_L"] = price_table[stock1+"_value"].shift(1) * price_table[stock1+"_log_ret"].shift(1) +  \
        price_table[stock2+"_value"].shift(1) * price_table[stock2+"_log_ret"].shift(1)
    else:    
        price_table[stock1+"_value"] = price_table[stock1+"_suggest_shares"].shift(1)*price_table[stock1+"_close"].shift(1)
        price_table[stock2+"_value"] = price_table[stock2+"_suggest_shares"].shift(1)*price_table[stock2+"_close"].shift(1)
        price_table["p_L"] = price_table[stock1+"_value"].shift(1) * price_table[stock1+"_log_ret"].shift(1)*price_table.trade.shift(1) +  \
        price_table[stock2+"_value"].shift(1) * price_table[stock2+"_log_ret"].shift(1)*price_table.trade.shift(1)

    print ("Finalizing, 90%")
    price_table["rolling_p_L"] = price_table.p_L.rolling(window).sum()
    return price_table