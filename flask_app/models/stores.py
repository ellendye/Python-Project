from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

import re
from flask import app, flash

class Store:
    def __init__(self, data):
        self.id = data['id']
        self.vendor_name = data['vendor_name']
        self.zip_code = data['zip_code']
        self.description = data['description']
        self.logo = data['logo']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.owner_id = None

    
    @classmethod
    def save_information(cls, data):
        query = "INSERT INTO vendors (vendor_name, zip_code, description, logo, owner_id) VALUES (%(vendor_name)s, %(zip_code)s, %(description)s, %(logo)s, %(owner_id)s);"
        
        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, data)
        
        return results

    @classmethod
    def get_vendor(cls, id):
        query = "SELECT vendors.id as id, vendor_name, zip_code, vendors.description as vendor_description, logo, owner_id, item_name, items.id as item_id, photo, price, items.description as item_description, stock FROM vendors LEFT JOIN items ON vendors.id = items.vendor_id WHERE owner_id = %(owner_id)s;"

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, id)

        return results


    @classmethod
    def get_vendor_by_store_id(cls, id):
        query = "SELECT vendors.id as id, vendor_name, zip_code, vendors.description as vendor_description, logo, owner_id, item_name, items.id as item_id, photo, price, items.description as item_description FROM vendors LEFT JOIN items ON vendors.id = items.vendor_id WHERE vendors.id = %(id)s;"

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, id)

        return results

    @classmethod
    def get_all_vendors(cls):
        query = "SELECT * FROM vendors"

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query)

        return results


    @classmethod
    def get_item_order_vendor(cls, id):
        query = "SELECT * FROM items LEFT JOIN items_in_order ON items.id = items_id LEFT JOIN orders ON orders.id = user_orders_id WHERE (items_id <> 'Null' AND vendor_id = %(owner_id)s);"

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, id)
        
        orders =[]
        for result in results: 
            orders.append(result)
        return orders

    @classmethod
    def update_store(cls, data):
        query = "UPDATE vendors SET vendor_name = %(vendor_name)s, zip_code = %(zip_code)s, description = %(description)s, logo = %(logo)s WHERE owner_id = %(owner_id)s;"

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, data)


        return results

    @staticmethod
    def validate_store(vendor):
        is_valid = True
        vendor_name = re.compile(r'^[a-zA-Z]{2,45}$')

        if not vendor_name.match(vendor['vendor_name']):
            flash("Invalid vendor name. Vendor name must be letters between 2-45 characters long")
            is_valid = False
        
        if len(vendor['zip_code']) < 5:
            flash("Invalid zip code. Zip code must be at least 5 numbers long")
            is_valid = False

        query = "SELECT vendor_name FROM vendors WHERE vendor_name = %(vendor_name)s;"
        modified_data = {
            'vendor_name': vendor['vendor_name']
        }
        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, modified_data)

        if len(results) > 0:
            is_valid = False
            flash("This shop name already exists. Please try something else.")

        return is_valid