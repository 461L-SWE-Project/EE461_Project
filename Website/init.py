from flask import Flask
from flask_pymongo import PyMongo
from os import path
from .auth import auth
from .project import project
from flask_cors import CORS

mongo = None

def createApp():
    app = Flask(__name__)
    ##used a test databse in my cluster for no2
    app.config["MONGO_URI"] = "mongodb+srv://threeMusketeers461:ee461l3@cluster0.o18a8.mongodb.net/Team_Project?retryWrites=true&w=majority"
    CORS(app)
    
    global mongo
    mongo = PyMongo(app)
    
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(project, url_prefix='/')
    return app
    
def getDatabase():
    return mongo