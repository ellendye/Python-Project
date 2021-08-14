from flask_app.models.stores import Store
from flask_app import app

from flask import render_template, redirect, session, request, flash, url_for
import urllib.request
import os
from werkzeug.utils import secure_filename
import random 
from random import randint

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'flask_app/static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask_app.models.users import User
from flask_app.models.items import Item


@app.route('/')
def index():

    all_vendors = Store.get_all_vendors()
    vendor_spotlight = []
    for i in range(0,3):
        x = randint(0,len(all_vendors)-1)
        vendor_spotlight.append(all_vendors[x])
    return render_template("index.html", random_vendors = vendor_spotlight)


@app.route('/login')
def login():

    if 'id' in session:
        return redirect('/dashboard')

    return render_template("login.html")


@app.route('/validate', methods=['POST'])
def validate_and_login():

    if request.form['which_form'] == 'registration':
        if not User.validate_registration(request.form):
            return redirect('/login')
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        
        data = {
            "first_name": request.form['first_name'], 
            "last_name": request.form['last_name'],
            "email": request.form['email'],
            "password": pw_hash
        }
        User.save_information(data)

    elif request.form['which_form'] =='login':
        user_in_db = User.validate_email(request.form)
        if not user_in_db:
            return redirect('/login')
        if not bcrypt.check_password_hash(user_in_db['password'], request.form['password']):
            flash("Invalid Password. Please enter again")
            return redirect('/login')
    
    user = User.get_user(request.form)
    
    session['id'] = user.id
    session['first_name'] = user.first_name

    modified_data = {
        'owner_id': session['id']
    }
    
    if len(Store.get_vendor(modified_data)) > 0:
        session['vendor'] = True


    return redirect('/dashboard')
    

@app.route('/dashboard')
def render_dashboard():

    if not 'id' in session:
        return redirect('/login')

    user = User.get_user_by_id(session['id'])
    orders = Item.get_order_by_user(session['id'])
    return render_template("dashboard.html", user=user, orders=orders)


@app.route('/dashboard/editprofile', methods=['POST'])
def edit_profile():

    if not 'id' in session: 
        return redirect('/')

    file = request.files['profile_picture']

    if file.filename == '':
        user = User.get_user_by_id(session['id'])
        if user.profile_picture != None:
            photo = user.profile_picture
        else: 
            photo = None
    

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # print('upload_image filename: ' + filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        photo = f"/static/uploads/{filename}"
    
    if not User.validate_updated_user(request.form, session['id']):
        return redirect('/dashboard')

    data = {
        "first_name": request.form['first_name'], 
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "profile_picture": photo, 
        "about_me": request.form['about_me'], 
        "birthday": request.form['birthday'],
        "id": session['id']
    }

    User.update_user(data)

    return redirect("/dashboard")


@app.route('/logout')
def log_out_user():

    session.clear()

    return redirect('/')