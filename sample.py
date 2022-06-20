import requests
import os
import json
import pprint


#const variables
api_key = "bNto50MTJRwuBR0eqJUVWUsGe"
api_key_secret = "qz72CdQXfgkJf6bvSvKy4Zj6EFEgisXTQQ1wNMJ6XOOJ3n8vFk"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAEsCcwEAAAAA8%2Fvq5bNbOZ899YVCTq1Y8y0uxoA%3DaTXsS7kWUIKeR4qs9WkFnlxZKNVedQ091aN6KUpD5RqjlZtJjU"
api_url = "https://api.twitter.com/2/"
sample_user_id = "704509563085586432"
endpoint = "https://api.twitter.com/2/tweets/search/recent"
tweet_field = "id,created_at,public_metrics,text,author_id,entities"
media_field = "media_key,preview_image_url,url"
merged_tweet_list = []


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

    print(iterator+"件発見", request_iterator + "回目のRequest")

    #Merge
    for media_id in media_list:
        for i in range(len(tweets_list)):
            if media_id[0] in tweets_list[i][0]:
                merged_tweet = tweets_list[i]
                merged_tweet_plus_url = merged_tweet + [media_id[1]]
                merged_tweet_list.append(merged_tweet_plus_url)
            else:
                pass
    print(merged_tweet_list)
       
def main():
    search_word = "PayPay  p活"
    print(search_word)
    search_url = endpoint + '?query={}%20-is%3Aretweet&expansions=author_id,attachments.media_keys&tweet.fields={}&media.fields={}&max_results=100'.format(search_word, tweet_field, media_field)
    json_response = get_tweets(search_url)
    print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()




# <div class="table-responsive">
#     <h1>{{ list_response | length }}件</h1>
#     <table class="table table-hover">
#         <thead class="thead-light">
#             <tr>
#                 <th scope="col">Tweet</th>
#                 <th scope="col">likes</th>
#                 <th scope="col">created_at</th>
#             </tr>
#         </thead>
#     <!-- DataTales Example style="font-size: 10pt; line-height: 140%;"-->
#         {% if list_response %} 
#         {% for tweet in list_response %}
#         {% if tweet[5] == "positive" %}
#             <tbody class="table">
#                 <tr>
#                     <td data-label="" style="word-break: break-word; word-wrap: break-word;">
#                         <a class="text-current" href="{{ tweet[0] }}">
#                             <p>{{ tweet[3] }}</p>
#                         </a>
#                     </td>
#                     <td data-label="">
#                         <span class="badge bg-soft-success text-success">{{ tweet[4] }}</span>
#                     </td>
#                     <td data-label="">
#                         <a class="text-current" href="#">{{ tweet[2] }}</a>
#                     </td>        
#                 </tr>
#             </tbody>
#         {% endif %}
#         {% else %}
#             <p>Undefined</p>
#         {% endfor %} 
#         {% endif %}
#     </table>
# </div>