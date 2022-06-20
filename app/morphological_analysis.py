from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.charfilter import *
from janome.tokenfilter import *
import itertools
import re

 
     
#https://qiita.com/charon/items/661d9a25b2233a9f8da4

tokenizer = Tokenizer()

def range_word_list(sentence):
    wide_range_pair_list = []
    sentence = re.sub(r'[!"“#$%&()\*\+\-\.,\/:;<=>?？！@\[\\\]^_`{|}~]', '', sentence)
    print("sentence", sentence)

    char_filters = [UnicodeNormalizeCharFilter(), RegexReplaceCharFilter('<.*?>', '')] #正規表現パターンにマッチした文字列を置換
    a = Analyzer(char_filters=char_filters, token_filters=[CompoundNounFilter(),POSKeepFilter(['名詞'])])
    search_noun_word = [token.surface for token in a.analyze(sentence)]
    wide_range_pair_list.append(sentence)

    #here is what to make change
    print(search_noun_word)
    for pair in itertools.combinations(search_noun_word, len(search_noun_word)-1):
        wide_range_pair_list.append(' '.join(list(pair)))
    return wide_range_pair_list