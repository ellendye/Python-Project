from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

import re
from flask import app, flash


class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.profile_picture = data['profile_picture']
        self.birthday = data['birthday']
        self.about_me = data['about_me']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    #method to add user to database. saves user information. password is already hashed.
    @classmethod
    def save_information(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"
        
        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, data)
        
        return results
    

    #method to retrieve a singular users information
    @classmethod
    def get_user(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s"

        modified_data= {
            'email': data['email']
        }

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, modified_data)
        
        if len(results) == 0:
            print("No user with that ID")
            return False

        user = cls(results[0])
        return user

    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s"

        modified_data = {
            "id": data
        }
        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, modified_data)
        print(results)
        if len(results) == 0:
            print("No user with that ID")
            return False

        user = cls(results[0])
        return user
    
    @classmethod
    def update_user(cls, data):
        query = "UPDATE users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s, profile_picture = %(profile_picture)s, about_me = %(about_me)s, birthday = %(birthday)s WHERE id = %(id)s;"

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, data)


        return results

    #validate user login method 
    @classmethod
    def validate_email(cls, data):
        query = "SELECT email, password FROM users WHERE email = %(email)s;"

        modified_data = {
            'email': data['email']
        }

        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, modified_data)

        if len(results) < 1:
            flash("This email does not exist, try again.")
            return False

        return results[0]


    #validate registration per the wireframe. CHANGE THIS IF WIREFRAME REQUIREMENTS CHANGE.
    @staticmethod
    def validate_registration(user):
        is_valid = True
        # test whether a field matches the patterns defined above
        email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
        first_name = re.compile(r'^[a-zA-Z]{2,45}$')
        last_name = re.compile(r'^[a-zA-Z]{2,45}$')

        if not email_regex.match(user['email']): 
            flash("Invalid email address!")
            is_valid = False
        if not first_name.match(user['first_name']):
            flash("Invalid first name. First name must be letters between 2-45 characters long")
            is_valid = False
        if not last_name.match(user['last_name']):
            flash("Invalid Last name. Last name must be letters between 2-45 characters long")
            is_valid = False
        #make sure password is at least 8 characters long
        if len(user['password']) < 8:
            flash("Invalid password. Password must be a minimum of 8 alphanumeric characters and a maximum of 45 characters")
            is_valid = False
        #make sure password matches the confirm password
        if not user['password'] == user['confirm_password']:
            flash("Passwords do not match. Please enter again.")
            is_valid = False
        
        #make sure email is unique
        query = "SELECT email FROM users WHERE email = %(email)s;"
        modified_data = {
            'email': user['email']
        }
        connection = connectToMySQL('final_project_python')
        results = connection.query_db(query, modified_data)

        if len(results) > 0:
            is_valid = False
            flash("This email already exists. Please log in to continue.")

        return is_valid

    
    @staticmethod
    def validate_updated_user(user, id):
        is_valid = True
        current_info = User.get_user_by_id(id)

        email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
        first_name = re.compile(r'^[a-zA-Z]{2,45}$')
        last_name = re.compile(r'^[a-zA-Z]{2,45}$')

        if not email_regex.match(user['email']): 
            flash("Invalid email address!")
            is_valid = False
        if current_info.email != user['email']:
            query = "SELECT email FROM users WHERE email = %(email)s;"
            modified_data = {
                'email': user['email']
            }
            connection = connectToMySQL('final_project_python')
            results = connection.query_db(query, modified_data)
            if len(results) > 0:
                is_valid = False
                flash("This email already exists. Please log in to continue.")
        if not first_name.match(user['first_name']):
            flash("Invalid first name. First name must be letters between 2-45 characters long")
            is_valid = False
        if not last_name.match(user['last_name']):
            flash("Invalid Last name. Last name must be letters between 2-45 characters long")
            is_valid = False

        return is_valid