from urllib import response
from app.sentiment_analysis import convert
import requests
import re


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
    positive_count = 0
    negative_count = 0
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
                if sentiment["top_class"] == "positive":
                    positive_count += 1
                if sentiment["top_class"] == "negative":
                    negative_count += 1
                if sentiment["classes"][0]["confidence"] >= 0.8 or sentiment["classes"][1]["confidence"] >= 0.8:
                    strength = 0
                    if sentiment["classes"][0]["confidence"] >= sentiment["classes"][1]["confidence"]:
                        strength = sentiment["classes"][0]["confidence"]
                    else:
                        strength = sentiment["classes"][1]["confidence"]
                    tweet.append("https://twitter.com/tweet/status/" + tweet_data["id"])
                    tweet.append(tweet_data["text"])
                    tweet.append(sentiment["top_class"])
                    tweet.append("検索ワード: " + search_word)
                    tweet.append('{:.0%}'.format(strength))
                    tweet.append(tweet_data["created_at"])
                    tweet.append(tweet_data["public_metrics"]["retweet_count"])
                    tweet.append(strength)
                    # tweet.append(tweet_data["public_metrics"]["reply_count"])
                    # tweet.append(tweet_data["author_id"])
                    tweets_list.append(tweet)
            except KeyError:
                tweet.append(" ")

        if request_iterator > 2:
            print('3リクエストを超えるため、中止します')
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

    print(str(iterator)+"件のツイート / " + str(request_iterator)+"回検索")
    return tweets_list, positive_count, negative_count

def sort_tweets(list):
    returning_list =[]
    sorted_list = sorted(list, reverse=True, key=lambda x: x[7])

    for sorted_tweet in sorted_list:
        if sorted_tweet[2] == "positive":
            returning_list.append(sorted_tweet)
            if len(returning_list) >= 9:
                break

    for sorted_tweet in sorted_list:
        if sorted_tweet[2] == "negative":
            returning_list.append(sorted_tweet)
            if len(returning_list) >= 9:
                break
    
    return returning_list


def trend():
    trend_list = []
    timeline_url = endpoint2 + nhk_news_twitter_id + "/tweets" + "?expansions=author_id,attachments.media_keys&tweet.fields={}&max_results=100&exclude=retweets,replies".format(tweet_field)

    # call endpoint
    trend_response = requests.get(timeline_url, auth=bearer_oauth)
    if trend_response.status_code != 200:
        if trend_response.status_code == 429:
            return "429"
        else:
            raise Exception(trend_response.status_code, trend_response.text)
    
    #orgnize list
    trend_data_response = trend_response.json()["data"]
    for trend_data in trend_data_response:
        trend = []
        try:
            if trend_data["entities"]["hashtags"][0]["tag"] == "nhk_news":
                trend.append(trend_data["text"][:-34])
                trend.append(trend_data["created_at"])
                trend.append(trend_data["public_metrics"]["like_count"])
                trend_list.append(trend)
        except KeyError:
            pass
    sorted_list = sorted(trend_list, reverse=True, key=lambda x: x[2])

    if len(sorted_list) >= 10:
        sorted_list = sorted_list[0:10]
    return sorted_list
