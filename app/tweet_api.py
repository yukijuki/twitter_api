from urllib import response
from app.sentiment_analysis import convert
import requests
import re
import pandas as pd



#const variables
api_key = "bNto50MTJRwuBR0eqJUVWUsGe"
api_key_secret = "qz72CdQXfgkJf6bvSvKy4Zj6EFEgisXTQQ1wNMJ6XOOJ3n8vFk"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAEsCcwEAAAAA8%2Fvq5bNbOZ899YVCTq1Y8y0uxoA%3DaTXsS7kWUIKeR4qs9WkFnlxZKNVedQ091aN6KUpD5RqjlZtJjU"

#Configs
endpoint = "https://api.twitter.com/2/tweets/search/recent"
endpoint2 = "https://api.twitter.com/2/users/"
nhk_news_twitter_id = "204245399"
tweet_field = "id,created_at,public_metrics,text,entities"
media_field = "media_key,preview_image_url,url"


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def get_tweets(search_word):

    search_url = endpoint + '?query={}%20-is%3Aretweet -is:retweet -is:reply&tweet.fields={}&max_results=100'.format(search_word, tweet_field)

    next_token_flag = True
    next_token = ""
    tweets_list = []
    iterator, request_iterator = 0, 0
    endpoint_url = search_url

    while next_token_flag:

        #check next token
        if next_token == "":
            pass
        else:
            endpoint_url = search_url + next_token

        # call endpoint
        response = requests.get(endpoint_url, auth=bearer_oauth)
        if response.status_code != 200:
            if response.status_code == 429:
                return "429"
            else:
                raise Exception(response.status_code, response.text)

        #orgnize list
        if response.json()["meta"]["result_count"] == 0:
            break
        data_response = response.json()["data"]
        for tweet_data in data_response:
            tweet = []
            try:
                sentiment = convert(tweet_data["text"])

                if sentiment["classes"][0]["confidence"] >= 0.8 or sentiment["classes"][1]["confidence"] >= 0.8:
                    strength = 0
                    if sentiment["classes"][0]["confidence"] >= sentiment["classes"][1]["confidence"]:
                        strength = sentiment["classes"][0]["confidence"]
                    else:
                        strength = sentiment["classes"][1]["confidence"]
                    tweet.append("https://twitter.com/tweet/status/" + tweet_data["id"])
                    tweet.append(tweet_data["text"])
                    tweet.append(sentiment["top_class"])
                    tweet.append('{:.0%}'.format(strength))
                    tweet.append(tweet_data["created_at"])
                    tweet.append(tweet_data["public_metrics"]["retweet_count"])
                    tweet.append(strength)
                    tweet.append(search_word)
                    # tweet.append(tweet_data["public_metrics"]["reply_count"])
                    # tweet.append(tweet_data["author_id"])
                    tweets_list.append(tweet)
            except KeyError:
                tweet.append(" ")
        
        
        if request_iterator > 4:
            print('5???????????????????????????????????????????????????')
            break

        #adding count
        request_iterator += 1
        iterator += response.json()['meta']['result_count']

        #handling pagination
        try:
            if response.json()["meta"]["next_token"]:
                next_token = '&pagination_token={}'.format(response.json()["meta"]["next_token"])
        except KeyError:
            next_token_flag = False

    print(str(iterator)+"?????????????????? / " + str(request_iterator)+"?????????")
    return tweets_list


def distinct_sort(tweet_list):
    positive_ratio = None
    negative_ratio = None

    df = pd.DataFrame(tweet_list, columns =['id','text','top_class', 'strength_in_%', 'created_at', 'retweet_count', 'strength', 'search_word'])
    distinct_df = df.drop_duplicates(subset='id')

    df_positive = distinct_df[distinct_df["top_class"] == "positive"].sort_values('strength', ascending=False).head(18).to_numpy().tolist()
    df_negative = distinct_df[distinct_df["top_class"] == "negative"].sort_values('strength', ascending=False).head(18).to_numpy().tolist()

    posi_nega_values = df[['top_class', 'strength']].groupby('top_class').sum()
    l_records = posi_nega_values.to_dict(orient='list')
    print(l_records)
    
    if len(l_records["strength"]) == 2:
        all_count = l_records["strength"][0] + l_records["strength"][1]
        positive_ratio = '{:.0%}'.format(l_records["strength"][1] / all_count)
        negative_ratio = '{:.0%}'.format(l_records["strength"][0] / all_count)

    return df_positive, df_negative, positive_ratio, negative_ratio