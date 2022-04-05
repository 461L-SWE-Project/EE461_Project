from flask import Blueprint, Flask, request
from flask_pymongo import PyMongo
from . import init
from . import encryption


auth = Blueprint('auth', __name__)


@auth.route('/')
def home():
    return "Home Page"

@auth.route('/register', methods=['POST'])
def register():
    if request.method == "POST":
        username = request.form.get['username']
        password = request.form.get['password']
        hashed_username = encryption.hash_string(username)
        mongo = init.getDatabase()
        users = mongo.db.user_authentication
        if users.find_one({"Username": hashed_username}) != None:
            return  {"Response": "Fail" , "Message": "Username already exists"}
        email = request.form['email']
        if '@' not in email or " " in email:
            return  {"Response": "Fail" , "Message": "Invalid email"}
        else:
            hashed_password = encryption.hash_string(password)
            post = {
                "Username" : hashed_username,
                "Password" : hashed_password,
                "Email" : email
            }
            users.insert_one(post)
            return  {"Response": "Success" , "Message": "Succesfully Created Account"}
    





