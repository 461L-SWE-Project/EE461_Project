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
    
    
@auth.route('/login', methods =['POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        # now checkign w encryption
        hashed_value_user = hash_string(user)
        hashed_value_pass = hash_string(password)
        
        #now search in database
        db = get_db()
        user_col = db.user_authentication
        if user_col.find({username: hashed_value_user, password: hashed_value_pass}).count() == 0:
            #return an error
            return {'Response': 'Fail', 'Message': 'Could not find username or password'}
    
        return {'Response': 'Success', 'Message': 'Successfully Logged in'}




# #this works
# @auth.route('/register/<username>')
# def register(username):
#     mongo = init.getDatabase()
#     users = mongo.db.user_authentication
#     hashed_username = encryption.hash_string(username)
#     if users.find_one({"Username": hashed_username}) != None:
#         return  {"Response": "Fail" , "Message": "Username already exists"}
#     else: 
#         post = {
#             "Username" : hashed_username,
#             "Password" : "Test123"
#         }
#         users.insert_one(post)
#         return  {"Response": "Success" , "Message": "Succesfully Created Account"}

# #this works as well
# @auth.route('/register/<username>/<password>')
# def register2(username,password):
#     mongo = init.getDatabase()
#     users = mongo.db.user_authentication
#     hashed_username = encryption.hash_string(username)
#     hashed_password = encryption.hash_string(password)
#     if users.find_one({"Username": hashed_username}) != None:
#         return  {"Response": "Fail" , "Message": "Username already exists"}
#     else: 
#         post = {
#             "Username" : hashed_username,
#             "Password" : hashed_password
#         }
#         users.insert_one(post)
#         return  {"Response": "Success" , "Message": "Succesfully Created Account"}