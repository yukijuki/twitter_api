from flask import request, render_template, session, redirect, url_for
from app import application
from app.tweet_api import get_tweets, distinct_sort
from app.morphological_analysis import range_word_list
from flask import flash



# @app.route("/", methods=["GET", "POST"])
# def index():
#     return render_template("index.html")

@application.route("/", methods=["GET"])
def home():
    #List preparartion
    returning_tweets_list = []
    list_of_search_word = []
    positive_ratio = None
    negative_ratio = None
    df_positive = []
    df_negative = []
    trend_list = []

    #trend_list = trend()

    #Return tweets found with search word
    passed_search_word = request.args.get('search_word')
    if passed_search_word is not None:
        print("passed_search_word", passed_search_word)
        list_of_search_word = range_word_list(passed_search_word)
        print("list_of_search_word", list_of_search_word)
        for search_word in list_of_search_word:
            tweet_info = get_tweets(search_word)
            if tweet_info == "429":
                redirect(url_for('rate_limit'))
            returning_tweets_list.extend(tweet_info)

        if len(returning_tweets_list) == 0:
            flash("検索結果が見つかりませんでした。")
        else:
            df_positive, df_negative, positive_ratio, negative_ratio = distinct_sort(returning_tweets_list)
    
    return render_template("index.html", df_positive = df_positive, df_negative = df_negative, list_of_search_word = list_of_search_word, negative_ratio=negative_ratio, trend_list=trend_list)


@application.route("/rate_limit", methods=["GET"])
def rate_limit():
    return render_template("rate_limit.html")

@application.route("/login", methods=["GET"])
def login():
    return render_template("login.html")