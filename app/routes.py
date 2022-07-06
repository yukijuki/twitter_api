from flask import request, session, render_template, redirect, url_for
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
    session_word_and_token = []
    next_pagination_values = None
    previous_pagination_values = None


    # sample
    paginations_sets_of_word_and_token = None

    trend_list = trend()

    #Return tweets found with search word
    passed_search_word = request.args.get('search_word')
    pagination_value = request.args.get('pagination_value')

    if passed_search_word is not None:
        print("passed_search_word", passed_search_word)
        
        if pagination_value is None:
            #analyze search word
            #need to add token to align
            list_of_search_word = range_word_list(passed_search_word)
            print("1st list_of_search_word", list_of_search_word)
        else:
            pagination_set = session.get('pagination_set')
            list_of_search_word = [one_set["search_word"] for one_set in pagination_set]
            print("2nd list_of_search_word", list_of_search_word)

        # get first tweets
        for search_word in list_of_search_word:

            pagination_token = None
            if pagination_value is not None:
                for one_set in session.get('pagination_set'):
                    if one_set["search_word"] == search_word:
                        pagination_token = one_set[pagination_value]
                        print("pagination_token_TEST", pagination_token)


            tweet_info, positive_count, negative_count, next_token, previous_token = get_tweets(search_word, pagination_token)
            if tweet_info == "429":
                redirect(url_for('rate_limit'))
            returning_tweets_list.extend(tweet_info)
            positive_total_count += positive_count
            negative_total_count += negative_count

            word_and_token = {
                "search_word": search_word,
                "next_token": next_token,
                "previous_token": previous_token
            }

            session_word_and_token.append(word_and_token)
            

        #organize
        if len(returning_tweets_list) == 0:
            flash("検索結果が見つかりませんでした。")
        else:
            print("Not distinct Tweest", len(returning_tweets_list))
            returning_distinct_tweets = list(map(list, set(map(tuple, returning_tweets_list))))
            print("distinct Tweest", len(returning_distinct_tweets))
            list_of_sorted_tweets = sort_tweets(returning_distinct_tweets)

            #hanlding posi nega ratio bar
            all_count = positive_total_count + negative_total_count
            positive_ratio = '{:.0%}'.format(positive_total_count / all_count)

            #set next pagination setting
            session['pagination_set'] = session_word_and_token
            next_pagination_values = [word_and_token["next_token"] for word_and_token in session_word_and_token if word_and_token["next_token"] is not None]
            previous_pagination_values = [word_and_token["previous_token"] for word_and_token in session_word_and_token if word_and_token["previous_token"] is not None]
            print("next_pagination_values", next_pagination_values)
            print("previous_pagination_values", previous_pagination_values)

    return render_template("index.html", list_response = list_of_sorted_tweets, list_of_search_word = list_of_search_word, positive_ratio=positive_ratio, trend_list=trend_list, next_pagination_values=next_pagination_values, previous_pagination_values = previous_pagination_values)


@app.route("/rate_limit", methods=["GET"])
def rate_limit():
    return render_template("rate_limit.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")