from asari.api import Sonar
sonar = Sonar()

def convert(tweet):
    class_response = sonar.ping(text=tweet)
    return class_response
