from flask_app import app

from flask import render_template, redirect, session, request, flash, url_for
import urllib.request
import os
from werkzeug.utils import secure_filename

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'flask_app/static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask_app.models.users import User
from flask_app.models.stores import Store
from flask_app.models.items import Item

@app.route('/search/custom', methods=['POST'])
def searchbar():

    item = request.form['srch-term']

    return redirect(f'/search/{item}')

@app.route('/search/<item>')
def search(item):

    results = Item.search_results(item)

    return render_template("search.html", items = results, search = item)

@app.route('/search/category/<item>')
def search_by_category(item):

    results = Item.search_results_by_category(item)

    return render_template("search.html", items=results, search = item)

@app.route('/vendor')
def render_become_vendor():
    if 'vendor' in session: 
        return redirect('/vendor/dashboard')
    return render_template("newvendor.html")

@app.route('/vendor/validate', methods=['POST'])
def validate_vendor():

    if 'vendor' in session: 
        redirect ('/vendor/dashboard')

    if not 'id' in session: 
        redirect ('/')

    if not Store.validate_store(request.form):
        return redirect('/vendor')

    if 'logo' not in request.files:
        flash('No file part')
        return redirect('/vendor')

    file = request.files['logo']

    if file.filename == '':
        flash('No image selected for uploading')
        return redirect('/vendor')
    

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # print('upload_image filename: ' + filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        photo = f"/static/uploads/{filename}"

    data = {
            "vendor_name": request.form['vendor_name'], 
            "description": request.form['description'],
            "zip_code": request.form['zip_code'],
            "logo": photo,
            "owner_id": session['id']
        }
    Store.save_information(data)
    session['vendor'] = True

    return redirect('/vendor/dashboard')

@app.route('/vendor/dashboard')
def render_vendor_template():
    if not 'vendor' in session:
        return redirect ('/dashboard')

    data = {
        "owner_id": session['id']
    }

    store_info = Store.get_vendor(data)
    
    order_info = Store.get_item_order_vendor(data)
    
    sales_data = [0,0]
    for order in order_info:
        sales_data[0] += 1
        sales_data[1] += int(order['total'])
    print(sales_data)

    return render_template("vendordashboard.html", store_info = store_info, order_info = order_info, sales_data = sales_data)

@app.route('/vendor/editprofile', methods = ['POST'])
def edit_vendor_profile():

    file = request.files['logo']

    if file.filename == '':
        modified_data ={
            'owner_id': session['id']
        }
        vendor = Store.get_vendor(modified_data)

        if vendor[0]['logo'] != None:
            photo = vendor[0]['logo']
        else: 
            photo = None
    

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # print('upload_image filename: ' + filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        photo = f"/static/uploads/{filename}"
    data = {
        'vendor_name': request.form['vendor_name'],
        'zip_code': request.form['zip_code'],
        'description': request.form['description'],
        'logo': photo,
        'owner_id': session['id']
    }

    Store.update_store(data)

    return redirect('/vendor/dashboard')

@app.route('/vendor/additem', methods=['POST'])
def add_item():
    

    if 'photo' not in request.files:
        flash('No file part')
        return redirect('/vendor/dashboard')

    file = request.files['photo']

    if file.filename == '':
        flash('No image selected for uploading')
        return redirect('/vendor/dashboard')
    

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # print('upload_image filename: ' + filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        photo = f"/static/uploads/{filename}"
        data = {
            "item_name": request.form['item_name'], 
            "description": request.form['description'],
            "price": request.form['price'],
            "photo": photo,
            "stock": request.form['stock'],
            "vendor_id": request.form['vendor_id']
        }

        Item.save_information(data, request.form)


        return redirect('/vendor/dashboard')
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect('/vendor/dashboard', filename = file.filename)

@app.route('/listing/<int:id>')
def render_item_page(id):

    item = Item.get_item(id)

    return render_template("viewlisting.html", item=item)

@app.route('/listing/<int:id>/add')
def add_item_to_cart(id):

    if not 'cart' in session: 
        session['cart'] = 1

    else: 
        session['cart'] += 1
    
    if not 'cart_items' in session: 
        session['cart_items'] = []
        session['cart_items'].append(id)
    else: 
        session['cart_items'].append(id)

    return redirect(f"/listing/{id}")

@app.route('/vendor/<int:id>')
def render_vendor_profile(id):

    data = {
        "id": id
    }

    store_info = Store.get_vendor_by_store_id(data)
    
    if not 'id' in session: 
        return render_template("vendorprofile.html", store_info = store_info)

    if store_info[0]['owner_id'] == session['id']:
        return redirect('/vendor/dashboard')

    return render_template("vendorprofile.html", store_info = store_info)


@app.route('/order/view/<int:id>')
def render_view_order(id):

    order = Item.get_items_in_order(id)
    data = {
        "addresses_id": order[0]['addresses_id'] 
    }
    address = Item.get_address_in_order(data)
    
    return render_template("vieworder.html", order = order, address = address[0])



@app.route('/cart')
def render_cart_template():

    
    items = []
    subtotal = 0
    if 'cart_items' in session:
        for item in range(len(session['cart_items'])):
        
            cart_item = Item.get_item(session['cart_items'][item])
            subtotal += cart_item['price']
            items.append(cart_item)

    return render_template("cart.html", items=items, subtotal=subtotal)

@app.route('/cart/remove/<int:id>')
def remove_item_from_cart(id):
    
    session['cart'] -= 1

    session['cart_items'].remove(id)

    return redirect("/cart")