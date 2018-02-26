import pymongo
from my_trader import *


class mongo:
    def __init__:


    def get_ondemand_quote(self,sym):
    api_key = 'b59b144a62e058b6c4e265c049dc679f'
    sym = "%2C".join(sym)
    # This is the required format for datetimes to access the API

    api_url = 'https://marketdata.websol.barchart.com/getQuote.csv?' +\
                    'apikey={}&symbols={}&mode=D'\
                         .format(api_key,sym)

    csvfile = pd.read_csv(api_url)
    csvfile = csvfile.rename({"symbol":"Ticker","serverTimestamp":"TimeStamp",\
                       "open":"Open","high":"High","low":"Low","close":"Close",\
                       "volume":"Volume","lastPrice":"Adj Close","netChange":"Return"},axis=1)
    #csvfile.set_index('timestamp', inplace=True)
    return csvfile

    def get_all_quote(self):
        result = pd.DataFrame()
        all_stock = pd.read_csv(directory + "Stock.csv")
        for i in range(199,len(all_stock),200):
            tic_list = all_stock.Ticker[i-199:i]
            result = result.append(get_ondemand_quote(tic_list))
        
        
        return result

    def query_database(self,stock, start_date = datetime.now()-timedelta(days =90),end_date=datetime.now()):
        client = pymongo.MongoClient()
        db = client["stocks_daily"]
        collection = db[stock]
        start_date = datetime.now()-timedelta(days =90)
        start_date=(start_date-datetime.utcfromtimestamp(0)).total_seconds()*1000
        end_date=datetime.now()
        end_date = (end_date-datetime.utcfromtimestamp(0)).total_seconds()*1000
        get = collection.find({"Ticker":stock,"TimeStamp":{"$gte":start_date,"$lt":end_date}}).sort("TimeStamp",pymongo.ASCENDING)
        get_frame = pd.DataFrame(list(get))
        get_frame[u'TimeStamp'] = get_frame[u'TimeStamp'].apply(lambda x: datetime.utcfromtimestamp(0) + timedelta(milliseconds= x))
        get_frame = get_frame.loc[:,["TimeStamp",'Adj Close','Close','High','Low','Open','Return','Ticker']]
        get_frame = get_frame.dropna()
        get_frame = get_frame.reindex()
        return get_frame

    def frame_to_mongo(self,data,collection):
        records = json.loads(data.T.to_json()).values()
        collection.insert(records)
    def update_db(self,stock):

        client = pymongo.MongoClient()
        db = client["stocks_daily"]
        collection = db[stock]
        quote = get_ondemand_quote([stock])
        quote['TimeStamp'].loc[0]  = datetime.strptime(quote['TimeStamp'][0][0:10],"%Y-%m-%d")
        quote = json.loads(quote.T.to_json()).values()[0]
        collection.update({"TimeStamp":quote[u'TimeStamp']},{"$set": quote },upsert=True)

    def delete_duplicates(self,collection):
        cursor = collection.aggregate(
            [
                {"$group": {"_id": "$TimeStamp", "unique_id": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
                {"$match": {"count": { "$gte": 2 }}}
            ]
        )

        response = []
        for doc in cursor:
            del doc["unique_id"][0]
            for id in doc["unique_id"]:
                response.append(id)

        collection.delete_many({"_id": {"$in": response}})