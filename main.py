from flask import Flask
from flask_pymongo import PyMongo
from os import path
from Website.init import createApp

app = createApp()


if __name__ == '__main__':
    app.run(host='0.0.0.0',port="5000",debug=True)