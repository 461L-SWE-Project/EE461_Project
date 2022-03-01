from flask import Flask, render_template
from flask_pymongo import PyMongo
import json



#add a PyMongo to our code (?)
app = Flask(__name__)
##used a test databse in my cluster for no2
app.config["MONGO_URI"] = "--enter URL--"
mongo = PyMongo(app)

#just for testing purposes
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
    item = db.test.find_one({"Name": "Test123"})
    str = "Name: " +item["Name"] +"\n\nBirthday: "+item["Birthday"]
    return str


