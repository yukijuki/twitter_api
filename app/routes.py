from flask import request, redirect, render_template
from app import app
from app.tweet_api import get_tweets, sort_tweets
from app.morphological_analysis import word_list


#Configs
endpoint = "https://api.twitter.com/2/tweets/search/recent"
tweet_field = "id,created_at,public_metrics,text,author_id,entities"
media_field = "media_key,preview_image_url,url"



@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if request.form:
            data = request.form
            search_word = data["search_word"]
            search_url = endpoint + '?query={}%20-is%3Aretweet&expansions=author_id&tweet.fields={}&max_results=100'.format(search_word, tweet_field)
            list_of_tweets = get_tweets(search_url)
            list_of_sorted_tweets = sort_tweets(list_of_tweets)

    return render_template("index.html", list_response = list_of_sorted_tweets)