from app.sentiment_analysis import convert
import requests


#const variables
api_key = "bNto50MTJRwuBR0eqJUVWUsGe"
api_key_secret = "qz72CdQXfgkJf6bvSvKy4Zj6EFEgisXTQQ1wNMJ6XOOJ3n8vFk"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAEsCcwEAAAAA8%2Fvq5bNbOZ899YVCTq1Y8y0uxoA%3DaTXsS7kWUIKeR4qs9WkFnlxZKNVedQ091aN6KUpD5RqjlZtJjU"


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def get_tweets(search_url):

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
                tweets_list.append(tweet)
            except KeyError:
                tweet.append(" ")
  
        request_iterator += 1
        if request_iterator >= 10: # 180requestを超えたら止める
            print('30リクエストを超えるため、中止します')
            break

        iterator += response.json()['meta']['result_count']

        #handling pagination
        try:
            if response.json()["meta"]["next_token"]:
                next_token = '&pagination_token={}'.format(response.json()["meta"]["next_token"])
        except KeyError:
            next_token_flag = False

    print(str(iterator)+"件のツイート", str(request_iterator)+"回目の検索")
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