from flask import Flask
from flask_pymongo import PyMongo
from os import path
from Website.init import createApp
from flask_jwt_extended import JWTManager

app = createApp()
app.config["JWT_SECRET_KEY"] = "super-secret" #change
jwt = JWTManager(app)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port="5000",debug=True)