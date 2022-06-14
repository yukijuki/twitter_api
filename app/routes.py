from flask import request, session, redirect, jsonify, render_template, Response, url_for, abort, flash
from app import app
import requests
import qrcode
import cv2

#const variables
api_key = "bNto50MTJRwuBR0eqJUVWUsGe"
api_key_secret = "qz72CdQXfgkJf6bvSvKy4Zj6EFEgisXTQQ1wNMJ6XOOJ3n8vFk"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAEsCcwEAAAAA8%2Fvq5bNbOZ899YVCTq1Y8y0uxoA%3DaTXsS7kWUIKeR4qs9WkFnlxZKNVedQ091aN6KUpD5RqjlZtJjU"
api_url = "https://api.twitter.com/2/"
sample_user_id = "704509563085586432"
endpoint = "https://api.twitter.com/2/tweets/search/recent"
tweet_field = "id,created_at,public_metrics,text,author_id,entities"
media_field = "media_key,preview_image_url,url"



def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(search_url):
    response = requests.get(search_url, auth=bearer_oauth)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def get_tweets(search_url):

    next_token_flag = True
    next_token = ""
    tweets_list =[]
    media_list = []
    iterator, request_iterator = 0, 0
    endpoint_url = search_url
    merged_tweet_list = []
    while next_token_flag:

        #check next token
        if next_token == "":
            pass
        else:
            endpoint_url = search_url + next_token

        # call endpoint
        print(endpoint_url)
        response = requests.get(endpoint_url, auth=bearer_oauth)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        #organize media
        media_response = response.json()["includes"]["media"]

        for media_data in media_response:
            media = []
            try:
                if media_data["url"]:
                    media.append(media_data["media_key"])
                    media.append(media_data["url"])
                    media_list.append(media)
            except KeyError:
                pass

        #orgnize list
        data_response = response.json()["data"]
        for tweet_data in data_response:
            tweet = []
            try:
                if tweet_data["entities"]["urls"]:
                    tweet.append(tweet_data["entities"]["urls"][0]["media_key"])
                    tweet.append(tweet_data["id"])
                    tweet.append(tweet_data["author_id"])
                    tweet.append(tweet_data["created_at"])
                    tweet.append(tweet_data["text"])
                    tweet.append(tweet_data["public_metrics"]["like_count"])
                    tweet.append(tweet_data["entities"]["urls"][0]["expanded_url"])
                    tweets_list.append(tweet)
                else:
                    tweet.append(" ")
            except KeyError: 
                pass
  
        request_iterator += 1
        if request_iterator >= 50: # 180requestを超えたら止める
            print('180リクエストを超えるため、15分間停止します...')
            break

        iterator += response.json()['meta']['result_count']

        #handling pagination
        try:
            if response.json()["meta"]["next_token"]:
                next_token = '&pagination_token={}'.format(response.json()["meta"]["next_token"])
        except KeyError:
            next_token_flag = False

    print(iterator, request_iterator)

    #Merge
    for media_id in media_list:
        for i in range(len(tweets_list)):
            if media_id[0] in tweets_list[i][0]:
                merged_tweet = tweets_list[i]
                merged_tweet_plus_url = merged_tweet + [media_id[1]]
                merged_tweet_list.append(merged_tweet_plus_url)
            else:
                pass
    return merged_tweet_list


@app.route("/", methods=["GET", "POST"])
def index():
    returning_list = ""
    qr_list = []
    if request.method == "POST":
        print("check")
        if request.form:
            data = request.form
            search_word = data["search_word"]
            print(search_word)
            search_url = endpoint + '?query={}%20-is%3Aretweet&expansions=author_id,attachments.media_keys&tweet.fields={}&media.fields={}&max_results=100'.format(search_word, tweet_field, media_field)
            list_response = get_tweets(search_url)
            print(len(list_response))

            d = cv2.QRCodeDetector()

            for response in list_response:
                
                obj = requests.get(response[7])
                if obj.status_code == 200:
                    with open('1.png', 'wb') as f:
                        f.write(obj.content)

                try:
                    img = cv2.imread('1.png')
                    val, points, straight_qrcode = d.detectAndDecode(img)
                    print(val)
                    if val[0:23] == "https://qr.paypay.ne.jp":
                        qr_list.append(response)
                except KeyError:
                    pass
    
    if len(qr_list) > 0:
        returning_list = qr_list
    return render_template("index.html", list_response = returning_list)




# @app.route("/", methods=["GET", "POST"])
# def index():
#     search_word = "PayPay  p活"
#     print(search_word)
#     search_url = endpoint + '?query={}%20-is%3Aretweet&expansions=author_id,attachments.media_keys&tweet.fields={}&media.fields={}&max_results=100'.format(search_word, tweet_field, media_field)
#     list_response = get_tweets(search_url)
#     return render_template("index.html", list_response = list_response)