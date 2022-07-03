from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.charfilter import *
from janome.tokenfilter import *
import itertools
import re

#https://qiita.com/charon/items/661d9a25b2233a9f8da4
#https://resanaplaza.com/2022/06/04/__trashed-2/

tokenizer = Tokenizer()
fliter_word_list = ["速報", "JUST", "IN"]

def range_word_list(sentence):
    wide_range_pair_list = []
    sentence = re.sub(r'[!"“#$%&()\*\+\-\.,\/:;<=>?？！@\[\\\]^_`{|}~]', '', sentence)
    print("sentence", sentence)

    char_filters = [UnicodeNormalizeCharFilter(), RegexReplaceCharFilter('<.*?>', '')] #正規表現パターンにマッチした文字列を置換
    a = Analyzer(char_filters=char_filters, token_filters=[CompoundNounFilter(),POSKeepFilter(['名詞'])])
    search_noun_word = [token.surface for token in a.analyze(sentence)]

    if len(search_noun_word) > 3:
        search_noun_word_replace = []
        for token in tokenizer.tokenize(sentence):
            print(token)
            if token.part_of_speech.split(',')[0] == "名詞" and token.part_of_speech.split(',')[1] in ["一般", "固有名詞"]:
                if token.surface not in fliter_word_list:
                    search_noun_word_replace.append(token.surface)
        search_noun_word = search_noun_word_replace

    
    if search_noun_word:
        if len(search_noun_word) < 3:
            for pair in itertools.combinations(search_noun_word, len(search_noun_word)):
                wide_range_pair_list.append(' '.join(list(pair)))
        else:
            for pair in itertools.combinations(search_noun_word, len(search_noun_word)-1):
                wide_range_pair_list.append(' '.join(list(pair)))
    return wide_range_pair_list