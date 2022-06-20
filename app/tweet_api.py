from urllib import response
from app.sentiment_analysis import convert
from flask import flash
import requests
import re


#const variables
api_key = "bNto50MTJRwuBR0eqJUVWUsGe"
api_key_secret = "qz72CdQXfgkJf6bvSvKy4Zj6EFEgisXTQQ1wNMJ6XOOJ3n8vFk"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAEsCcwEAAAAA8%2Fvq5bNbOZ899YVCTq1Y8y0uxoA%3DaTXsS7kWUIKeR4qs9WkFnlxZKNVedQ091aN6KUpD5RqjlZtJjU"

#Configs
endpoint = "https://api.twitter.com/2/tweets/search/recent"
tweet_field = "id,created_at,public_metrics,text,author_id,entities"
media_field = "media_key,preview_image_url,url"


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def get_tweets(search_word):

    print(search_word)
    search_word = re.sub(r'[!"“#$%&()\*\+\-\.,\/:;<=>?@\[\\\]^_`{|}~]', '', search_word)
    search_url = endpoint + '?query={}%20-is%3Aretweet&expansions=author_id&tweet.fields={}&max_results=100'.format(search_word, tweet_field)

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
            raise Exception(response.status_code, response.text)

        #orgnize list
        if response.json()["meta"]["result_count"] == 0:
            flash("ツイートが見つかりません！")
            break
        data_response = response.json()["data"]
        for tweet_data in data_response:
            tweet = []
            try:
                tweet.append("https://twitter.com/tweet/status/" + tweet_data["id"])
                tweet.append(tweet_data["author_id"])
                tweet.append(tweet_data["created_at"])
                tweet.append(tweet_data["text"])
                tweet.append(tweet_data["public_metrics"]["like_count"])
                tweet.append(tweet_data["public_metrics"]["reply_count"])
                sentiment = convert(tweet_data["text"])
                tweet.append(sentiment["top_class"])
                tweet.append("検索ワード: " + search_word)
                tweets_list.append(tweet)
            except KeyError:
                tweet.append(" ")
  
        if request_iterator > 5: # 180requestを超えたら止める
            print('5リクエストを超えるため、中止します')
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

    print(str(iterator)+"件のツイート / " + str(request_iterator)+"回目の検索")
    return tweets_list

def sort_tweets(list):
    returning_list =[]
    sorted_list = sorted(list, reverse=True, key=lambda x: x[4])

    for sorted_tweet in sorted_list:
        if sorted_tweet[6] == "positive":
            returning_list.append(sorted_tweet)
            if len(returning_list) >= 10:
                break

    for sorted_tweet in sorted_list:
        if sorted_tweet[6] == "negative":
            returning_list.append(sorted_tweet)
            if len(returning_list) >= 20:
                break
    
    print(returning_list)

    return returning_list


def trend():
    trend_response = requests.get("https://api.twitter.com/1.1/trends/place.json?id=23424856", auth=bearer_oauth)
    if trend_response.status_code != 200:
            raise Exception(trend_response.status_code, trend_response.text)
    return  trend_response