from janome.tokenizer import Tokenizer
#https://qiita.com/charon/items/661d9a25b2233a9f8da4

tokenizer = Tokenizer()

def word_list():

    sentenses = [
        "ギョエェェエーと叫ぶだけの人生だった。",
        "最終兵器は懐にしまいます。",
        "お前は助からない。",
        "ログを読め。",
        "さあご一緒に！「TRUE 1 が TRUE！ TRUE 0 が FALSE！」"
    ]

    for sentence in sentenses:
        print("=============================================")
        print(sentence)

        for token in tokenizer.tokenize(sentence):
            print("    " + str(token))
    return "Resolve"