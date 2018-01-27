"""
[u'24h_volume_usd', u'available_supply', u'id', u'last_updated',
       u'market_cap_usd', u'max_supply', u'name', u'percent_change_1h',
       u'percent_change_24h', u'percent_change_7d', u'price_btc', u'price_usd',
       u'rank', u'symbol', u'total_supply']
"""

import  pandas as pd
import time

from utils import *
from email_sender import *

#check if price %change is more than 10% and send email
def get_crypto_data(cryto_df,interval, old_price,old_vol, old_rank):

    new_price = cryto_df.price_usd
    ticker = cryto_df.symbol
    name = cryto_df.id
    #updated_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cryto_df.last_updated))
    updated_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    new_vol = cryto_df["24h_volume_usd"]
    new_rank = cryto_df["rank"]

    # Logic for Percentage change decider
    perc_change_n_mins = get_percentage_change(old_price, new_price)
    vol_per_change = get_percentage_change(old_vol, new_vol)
    rank_change = get_rank_changed(old_rank, new_rank)

    return (ticker, name, perc_change_n_mins, new_price, vol_per_change, rank_change, updated_time)

    """
    if (perc_change_n_mins > 5):
        #Send email if significant change in price
        body = get_html_response(ticker, name, perc_change_n_mins, new_price, vol_per_change, updated_time )

        recipients = ['dhrumin.desai28@gmail.com','rutvi.doshi126@gmail.com','nevil.nayak@gmail.com']
        sender = "dhrumin.desai28@gmail.com"
        subject = "Crypto price alert"

        send_email(sender, recipients, subject, body)
        print body
    """


#-------------------------------------------------------------------------------------------------------------------------
#dump data into csv
def dump_to_csv(topNTickers,interval_mins):

    prev_per_change_dict = {}
    prev_vol = {}

    while True:

        crypto_data_list = []

        for id in get_top_n_tickers(topNTickers):

            #initializaton for all tickers
            if id not in prev_per_change_dict: prev_per_change_dict[id] = -1
            if id not in prev_vol: prev_vol[id] = -1

            #load the data
            cryto_df = pd.read_json("https://api.coinmarketcap.com/v1/ticker/"+id+"/")

            #check if the price % change is more than 10%
            price_change = get_percentage_change(prev_per_change_dict[id] , cryto_df.price_usd[0])
            if(price_change >= 10 or price_change <= -10):
                crypto_data_list.append(get_crypto_data(cryto_df,interval_mins, prev_per_change_dict[id],prev_vol[id],))

            prev_per_change_dict[id] = cryto_df.price_usd[0]
            prev_vol[id] = cryto_df["24h_volume_usd"][0]

            with open("../resource/cryptos/"+id+".csv", "a") as f:
                cryto_df.to_csv(f, header=False,index=False)


        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cryto_df.last_updated)))

        #Send an email
        if crypto_data_list:
            email_response = get_html_response(crypto_data_list)
            print ("sent")
            recipients = get_recipients()
            sender = "dhrumin.desai28@gmail.com"
            subject = "Crypto price alert"
            send_email(sender, recipients, subject, email_response)

        time.sleep(interval_mins*60)

# New method for notyfying all cryptos

def process_all_cryptos(interval_mins):
    prev_per_change_dict = {}
    prev_vol = {}
    prev_rank = {}

    while True:

        crypto_data_list = []
        cryto_df = pd.read_json("https://api.coinmarketcap.com/v1/ticker/?limit=0")

        for idx, row in cryto_df.iterrows():

            # initializaton for all tickers
            if row.id not in prev_per_change_dict: prev_per_change_dict[id] = -1
            if row.id not in prev_vol: prev_vol[id] = -1
            if row.id not in prev_rank: prev_rank[id] = 0


            # check if the price % change is more than 10%
            price_change = get_percentage_change(prev_per_change_dict[id], row.price_usd)
            if (price_change >= 5):
                crypto_data_list.append(
                    get_crypto_data(row, interval_mins, prev_per_change_dict[id], prev_vol[id], prev_rank[id]))

            prev_per_change_dict[id] = row.price_usd
            prev_vol[id] = row["24h_volume_usd"]
            prev_rank[id] = row["rank"]
            sorted_by_price = sorted(crypto_data_list, key=lambda tup: tup[3],reverse=True)
            
            
        # Send an email
        if crypto_data_list:
            email_response = get_html_response(sorted_by_price[:50])
            recipients = get_recipients()
            sender = "dhrumin.desai28@gmail.com"
            subject = "DDCryptoAlert"
            send_email(sender, recipients, subject, email_response)
            print ("sent")

        time.sleep(interval_mins * 60)


process_all_cryptos(interval_mins = 60)

#print (crytos_df.percent_change_1h)





