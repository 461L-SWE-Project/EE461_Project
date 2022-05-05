from sys import stderr
from flask import Blueprint, Flask, request, make_response
from flask_pymongo import PyMongo
from . import init
from . import encryption
import json
import jwt
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity


auth = Blueprint('auth', __name__)


# @auth.route('/') # Maybe we should register this without the blueprint, since this isn't really an auth module route - SIDHARTH
# def home():
#     return "Home Page"

@auth.route('/register', methods=['POST'])
def register():
    if request.method == "POST":
        username = request.json['username']
        password = request.json['password']
        hashed_username = encryption.hash_string(username)
        mongo = init.getDatabase()
        users = mongo.db.user_authentication
        hardware = mongo.db.hardware_resources
        if users.find_one({"username": username}) != None:
            return  {"Response": False , "Message": "Username already exists"}
        # email = request.form['email']
        # if '@' not in email or " " in email:
        #     return  {"Response": False , "Message": "Invalid email"}
        else:
            hashed_password = encryption.hash_string(password)

            #user has not checked out any hardware yet
            HW_Dict = {}
            for document in hardware.find():
                HW_Dict[document["name"]] = 0
            
            post = {
                "username" : username,
                "password" : hashed_password,
                # "Email" : email
                "checked_out_hardware":HW_Dict,
                "projects": []
            }
            users.insert_one(post)
            
              #creating JWT token
            active_col = mongo.db.active_users 
            access_token = create_access_token(identity=username)
            active_post = {
                "token_id": access_token,
                "username": username
            }
            active_col.insert_one(active_post)
            return  {"Response": True , "Message": "Succesfully Created Account", "token": access_token}
            # return  {"Response": True , "Message": "Succesfully Created Account"} #Should return a JWT here as well because we're going to log the user in
    
    
@auth.route('/authenticate', methods =['POST'])
def login():
    # debug = json.loads(request)
    # auth.logger.info(debug)
    if request.method == 'POST':
        user = request.json['username']
        password = request.json['password']
        # now checking w encryption
        hashed_value_user = encryption.hash_string(user)
        hashed_value_pass = encryption.hash_string(password)
        
        #now search in database
        mongo = init.getDatabase()
        user_col = mongo.db.user_authentication
        print(user_col.find_one({"username": user, "password": hashed_value_pass}),stderr)
        if user_col.find_one({"username": user, "password": hashed_value_pass}) == None: #Changed JSON field names to strings, not sure if they need to be variables, but it made the error go away - Sidharth
            #return an error
            return {'Response': False, 'Message': 'Could not find username or password'}
    
        #creating JWT token
        active_col = mongo.db.active_users 
        access_token = create_access_token(identity=user)
        active_post = {
            "token_id": access_token,
            "username": user
        }
        active_col.insert_one(active_post)
     
        return {"Response": True, 'Message': 'Successfully Logged in', 'token':access_token} #Sidharth - We need to track logins somehow in order to validate project / dataset requests that are coming in.


@auth.route('/logout', methods =['POST'])
@jwt_required()
def logout():
    if request.method == 'POST':
        current_user_id = get_jwt_identity()
        print(current_user_id)
        #delete from active users
        mongo = init.getDatabase()
        active_col = mongo.db.active_users 
        active_col.delete_one(active_col.find_one({'username': current_user_id}))
        return {"Response": True, "Message": "Successfully logged out"}
    
@auth.route('/timeout', methods =['POST'])
def timeout():
    if request.method == 'POST':
        # user_id = request.json["username"]
        # mongo = init.getDatabase()
        # active_col = mongo.db.active_users 
        # active_col.delete_one(active_col.find_one({'username': user_id}))
        print("am i even reaching")
        return {"Response": True, "Message": "User logged out due to inactivity"}
        # return {"Response": True, "Message": "User logged out due to inactivity"}
    

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