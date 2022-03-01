from flask import Flask, render_template
from flask_pymongo import PyMongo
import json



#add a PyMongo to our code (?)
app = Flask(__name__)
##used a test databse in my cluster for no2
app.config["MONGO_URI"] = "mongodb+srv://nidhid01:hello1234562001@422-cluster.qme7d.mongodb.net/gettingStartedSp22?retryWrites=true&w=majority"
mongo = PyMongo(app)


@app.route('/')
def hello():
    db = mongo.db
    post = {
        "Name": "Test123",
        "Birthday": "01/01/2001"
    }
    #insert a document in test collection
    db = mongo.db
    db.test.insert_one(post)
    #find document in test collection
    item = db.test.find_one({"Name": "Nidhi Dubagunta"})
    str = "Name: " +item["Name"] +"\n\nBirthday: "+item["Birthday"]
    return str


