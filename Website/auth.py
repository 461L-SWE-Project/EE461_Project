from flask import Blueprint, Flask, request
from flask_pymongo import PyMongo
from . import init
from . import encryption


auth = Blueprint('auth', __name__)


# @auth.route('/')
# def home():
#     return "Home Page"

# @auth.route('/register', methods=['POST'])
# def register():
#     if request.method == "POST":
#         username = request.form['username']
#         password = request.form['password']
#         hashed_username = encryption.hash_string(username)
#         mongo = init.getDatabase()
#         users = mongo.db.user_authentication
#         if users.find_one({"Username": hashed_username}) != None:
#             return  {"Response": "Fail" , "Message": "Username already exists"}
#         email = request.form['email']
#         if '@' not in email or " " in email:
#             return  {"Response": "Fail" , "Message": "Invalid email"}
#         else:
#             hashed_password = encryption.hash_string(password)
#             post = {
#                 "Username" : hashed_username,
#                 "Password" : hashed_password,
#                 "Email" : email
#             }
#             users.insert_one(post)
#             return  {"Response": "Success" , "Message": "Succesfully Created Account"}
#     # elif request.method == "GET":
#     #     return "Display Register Page(I think thats on the frontend side--don't have to render a template)"





#this works
@auth.route('/register/<username>')
def register(username):
    mongo = init.getDatabase()
    users = mongo.db.user_authentication
    hashed_username = encryption.hash_string(username)
    if users.find_one({"Username": hashed_username}) != None:
        return  {"Response": "Fail" , "Message": "Username already exists"}
    else: 
        post = {
            "Username" : hashed_username,
            "Password" : "Test123"
        }
        users.insert_one(post)
        return  {"Response": "Success" , "Message": "Succesfully Created Account"}

#this works as well
@auth.route('/register/<username>/<password>')
def register2(username,password):
    mongo = init.getDatabase()
    users = mongo.db.user_authentication
    hashed_username = encryption.hash_string(username)
    hashed_password = encryption.hash_string(password)
    if users.find_one({"Username": hashed_username}) != None:
        return  {"Response": "Fail" , "Message": "Username already exists"}
    else: 
        post = {
            "Username" : hashed_username,
            "Password" : hashed_password
        }
        users.insert_one(post)
        return  {"Response": "Success" , "Message": "Succesfully Created Account"}
