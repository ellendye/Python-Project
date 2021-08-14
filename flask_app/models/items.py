from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from random import randint

import re
from flask import app, flash

class Item:
    def __init__(self, data):
        self.id = data['id']
        self.item_name = data['item_name']
        self.price = data['price']
        self.description = data['description']
        self.photo = data['photo']
        self.stock = data['stock']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.vendor_id = None


    @classmethod
    def save_information(cls, data, data2):
        query = "INSERT INTO items (item_name, price, description, photo, stock, vendor_id) VALUES (%(item_name)s, %(price)s, %(description)s, %(photo)s, %(stock)s, %(vendor_id)s);"
        
        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, data)
        
        item_id = results
        
        items_categories = []
        for category in data2.getlist('category'):
            items_categories.append({'categories_id': int(category)+9, 'items_id':item_id})
        print(items_categories)
        query2 = "INSERT INTO items_has_categories (categories_id, items_id) VALUES (%(categories_id)s, %(items_id)s);"
        for x in items_categories:
            connection = connectToMySQL('final_project_python')
            results2 = connection.query_db(query2, x)
            print(results2)

        return results
    
    @classmethod
    def get_item(cls, id):
        query = "SELECT * FROM items LEFT JOIN vendors ON vendors.id = items.vendor_id WHERE items.id = %(id)s;"

        modified_data = {
            'id': id
        }

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, modified_data)

        print(results)
        return results[0]
    
    @classmethod
    def search_results(cls, item): 
        query = "SELECT * FROM items LEFT JOIN vendors ON vendor_id = vendors.id WHERE item_name LIKE '%%%s%%';"
        query2 = "SELECT * FROM items LEFT JOIN vendors ON vendor_id = vendors.id WHERE items.description LIKE '%%%s%%';"
        query3 = "SELECT * FROM items LEFT JOIN items_has_categories ON items_id = items.id LEFT JOIN categories ON categories_id = categories.id WHERE category_name LIKE '%%%s%%';"
        print(item)
        modified_item = [item]
        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query % tuple(modified_item))
        connection = connectToMySQL('final_project_python')
        results2 = connection.query_db(query2 % tuple(modified_item))
        connection = connectToMySQL('final_project_python')
        results3 = connection.query_db(query3 % tuple(modified_item))
        
        results_array = []
        for result in results:
            results_array.append(result)

        results2_array = []
        for result in results2: 
            results2_array.append(result)
        
        results3_array = []
        for result in results3: 
            results3_array.append(result)

        for x in results2_array:
            if x not in results_array:
                results_array.append(x)
        
        for x in results3_array:
            if x not in results_array:
                results_array.append(x)
        
        return results_array

    @classmethod
    def search_results_by_category(cls, item):
        query = "SELECT * FROM items LEFT JOIN items_has_categories ON items_id = items.id LEFT JOIN categories ON categories_id = categories.id WHERE category_name = %(category_name)s;"

        if item == 'random': 
            x = randint(0, 10)
            cats = ['jewelry', 'furniture', 'antiques', 'games', 'Handcrafted Goods', 'clothing', 'home decor', 'outdoor', 'party supplies']
            item = cats[x]
            modified_results = {
                'category_name': item
            }
        else: 
            modified_results = {
                'category_name': item
            }
        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, modified_results)

        items = []
        for result in results: 
            items.append(result)

        return items

    @classmethod
    def new_order(cls, id, items, total, address):
        query3 = "INSERT INTO addresses (address_1, address_2, city, state, zip_code) VALUES (%(address_1)s, %(address_2)s, %(city)s, %(state)s, %(zip_code)s);"

        modified_address = {
            'address_1': address['address_1'],
            'address_2': address['address_2'],
            'city': address['city'],
            'state': address['state'],
            'zip_code': address['zip_code']
        }

        connection = connectToMySQL('final_project_python')
        results3 = connection.query_db(query3,modified_address)
        address_id = results3


        query = "INSERT INTO orders (user_id, total, addresses_id) VALUES (%(user_id)s, %(total)s, %(address_id)s);"

        data = {
            'user_id': id,
            'total': total,
            'address_id': address_id
        }

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, data)

        order_id = results

        items_in_order = []
        for item in items:
            items_in_order.append({'items_id': item, 'user_orders_id': order_id})

        query2 = "INSERT INTO items_in_order (items_id, user_orders_id) VALUES (%(items_id)s, %(user_orders_id)s);"
        for x in items_in_order:
            connection = connectToMySQL('final_project_python')
            results2 = connection.query_db(query2, x)
            print(results2)
        
        return results


    @classmethod
    def get_order_by_user(cls, id):
        query = "SELECT * FROM orders WHERE user_id = %(user_id)s;"

        data = {
            'user_id': id
        }

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, data)

        orders = []
        for result in results:
            orders.append(result)

        return orders


    @classmethod
    def get_items_in_order(cls, id):
        query = "SELECT * FROM orders LEFT JOIN items_in_order ON user_orders_id = orders.id LEFT JOIN items ON items_id = items.id WHERE orders.id = %(id)s;"

        data = {
            'id': id
        }

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, data)

        orders = []
        for result in results:
            orders.append(result)

        return orders

    @classmethod
    def get_address_in_order(cls, id):
        query = "SELECT * FROM addresses LEFT JOIN orders ON addresses_id = addresses.id WHERE addresses_id = %(addresses_id)s;"

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, id)

        return results