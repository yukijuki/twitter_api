from flask import Flask


app = Flask(__name__)
app.config["SECRET_KEY"] = "superSecret"
app.debug = True

from app import routes  
