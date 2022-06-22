from flask import request, render_template
from app import app
from app.tweet_api import get_tweets, sort_tweets, trend
from app.morphological_analysis import range_word_list
from flask import flash



# @app.route("/", methods=["GET", "POST"])
# def index():
#     return render_template("index.html")

@app.route("/", methods=["GET", "POST"])
def home():
    #List preparartion
    returning_tweets_list = []
    list_of_sorted_tweets = []
    list_of_search_word = []

    # trend_list = trend()
    # print(trend_list)
    if request.method == "POST":
        if request.form:
            data = request.form
            passed_search_word = data["search_word"]
            list_of_search_word = range_word_list(passed_search_word)
            print(list_of_search_word)
            for search_word in list_of_search_word:
                list_of_tweets = get_tweets(search_word)
                returning_tweets_list.extend(list_of_tweets)

            if len(returning_tweets_list) == 0:
                flash("検索結果が見つかりませんでした。")
            else:
                returning_distinct_tweets = list(map(list, set(map(tuple, returning_tweets_list))))
                list_of_sorted_tweets = sort_tweets(returning_distinct_tweets)

    return render_template("index.html", list_response = list_of_sorted_tweets, list_of_search_word = list_of_search_word)
