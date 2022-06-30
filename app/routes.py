from flask import request, render_template, session, redirect, url_for
from app import app
from app.tweet_api import get_tweets, sort_tweets, trend
from app.morphological_analysis import range_word_list
from flask import flash



# @app.route("/", methods=["GET", "POST"])
# def index():
#     return render_template("index.html")

@app.route("/", methods=["GET"])
def home():
    #List preparartion
    returning_tweets_list = []
    list_of_sorted_tweets = []
    list_of_search_word = []
    positive_total_count = 0
    negative_total_count = 0
    positive_ratio = None

    #Return tweets found with search word
    passed_search_word = request.args.get('search_word')
    if passed_search_word is not None:
        print("passed_search_word", passed_search_word)
        list_of_search_word = range_word_list(passed_search_word)
        print(list_of_search_word)
        for search_word in list_of_search_word:
            tweet_info, positive_count, negative_count = get_tweets(search_word)
            if tweet_info == "429":
                redirect(url_for('rate_limit'))
            returning_tweets_list.extend(tweet_info)
            positive_total_count += positive_count
            negative_total_count += negative_count

        if len(returning_tweets_list) == 0:
            flash("検索結果が見つかりませんでした。")
        else:
            returning_distinct_tweets = list(map(list, set(map(tuple, returning_tweets_list))))
            list_of_sorted_tweets = sort_tweets(returning_distinct_tweets)

            #hanlding posi nega ratio bar
            all_count = positive_total_count + negative_total_count
            positive_ratio = '{:.0%}'.format(positive_total_count / all_count)

    return render_template("index.html", list_response = list_of_sorted_tweets, list_of_search_word = list_of_search_word, positive_ratio=positive_ratio)


@app.route("/rate_limit", methods=["GET"])
def rate_limit():
    return render_template("rate_limit.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")