from flask import request, redirect, render_template, Response, url_for, abort, flash
from app import app
import requests
from app.tweet_api import get_tweets

#Configs
endpoint = "https://api.twitter.com/2/tweets/search/recent"
tweet_field = "id,created_at,public_metrics,text,author_id,entities"
media_field = "media_key,preview_image_url,url"



@app.route("/", methods=["GET", "POST"])
def index():
    list_response = []
    if request.method == "POST":
        if request.form:
            data = request.form
            search_word = data["search_word"]
            print(search_word)
            search_url = endpoint + '?query={}%20-is%3Aretweet&expansions=author_id,attachments.media_keys&tweet.fields={}&media.fields={}&max_results=100'.format(search_word, tweet_field, media_field)
            list_response = get_tweets(search_url)
            print(len(list_response))

    return render_template("index.html", list_response = list_response)

