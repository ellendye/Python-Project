from flask_app import app

from flask import render_template, redirect, session, request, flash, url_for
import os
import stripe

from flask_app.models.users import User
from flask_app.models.stores import Store
from flask_app.models.items import Item


stripe.api_key = 'sk_test_51J8EIDKLPBStFAqcTzrZJanyYAhTE6QJHOkYmoAiImuzCC96b9sKzOc9IMV5Ruu3Xm9Qq8Q1Vdj3ZLgcD2wPPo8e00Jk97pDj7'

YOUR_DOMAIN = 'http://localhost:5000'


@app.route('/cart/checkout', methods = ['POST'])
def create_checkout_session():
    subtotal = int(request.form['subtotal']) * 100
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': subtotal,
                    'product_data': {
                        'name': 'item(s) total',
                        'images': ['https://i.imgur.com/EHyR2nP.png'],
                    }
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url=YOUR_DOMAIN + '/success',
        cancel_url=YOUR_DOMAIN + '/cancel',
    )
    session['successful_checkout'] = request.form
    print(session)
    return redirect(checkout_session.url, code=303)

@app.route('/cancel')
def cancel_checkout():
    session.pop('successful_checkout')
    return redirect('/cart')

@app.route('/success')
def successful_checkout():

    subtotal = session['successful_checkout']['subtotal']
    number_of_items = session['cart']
    session.pop('cart')
    items = []
    for item in session['cart_items']:
        items.append(Item.get_item(item))
    order_num = Item.new_order(session['id'], session['cart_items'], subtotal, session['successful_checkout'])
    session.pop('cart_items')
    shipping_address = f"{session['successful_checkout']['address_1']} {session['successful_checkout']['address_2']} {session['successful_checkout']['city']} {session['successful_checkout']['state']}  {session['successful_checkout']['zip_code']}"
    session.pop('successful_checkout')
    print(session)

    return render_template("success.html", total = subtotal, number_of_items = number_of_items, items = items, order_num = order_num, shipping_address = shipping_address)