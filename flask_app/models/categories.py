from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL


import re
from flask import app, flash

class Category:
    def __init__(self, data):
        self.id = data['id']
        self.category_name = data['category_name']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']