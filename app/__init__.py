from flask import Flask


application= Flask(__name__)
application.config["SECRET_KEY"] = "superSecret"
application.debug = True

from app import routes  
