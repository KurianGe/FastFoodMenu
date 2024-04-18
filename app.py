from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import requests
import logging


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Logging configuration
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

# API endpoints
PRODUCT_ALLERGEN_API_URL = "https://d8dxl08wv3.execute-api.us-east-1.amazonaws.com/staging1/allergen-api/"
COUPON_API_URL = "https://w3d1szbsy8.execute-api.us-east-1.amazonaws.com/prod/coupon-api/?coupon_id=AllergenCoupon02"
EVENT_API_URL = "https://xzc3sw72c3.execute-api.eu-west-1.amazonaws.com/test/events/ALLERGEN01"

# Database initialization
def initialize_database():
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS menu_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price REAL, rating REAL DEFAULT 0)''')
    conn.commit()
    conn.close()

initialize_database()

# Database helper functions
def add_user_to_database(username, password):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def get_user_from_database(username):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_events():
    response = requests.get(EVENT_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        return None

#login function
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_from_database(username)
        if user and user[2] == password:  # user[2] is the password field in the database
            session['logged_in'] = True
            session['username'] = username  # Store the username in the session
            return redirect(url_for('index'))
    return render_template('login.html')

#signup function
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not get_user_from_database(username):
            add_user_to_database(username, password)
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', message='Username already exists. Please choose a different one.')
    return render_template('signup.html')

#signout function
@app.route('/signout')
def signout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# Secure the menu and coupon endpoints
def login_required(route_function):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return route_function(*args, **kwargs)
    wrapper.__name__ = route_function.__name__
    return wrapper

#calling the show_coupon API
@app.route('/show_coupon')
@login_required
def show_coupon():
    response = requests.get(COUPON_API_URL)
    if response.status_code == 200:
        coupon_info = response.json()
        app.logger.info("API call to COUPON_API_URL successful")
        return render_template('show_coupon.html', coupon_info=coupon_info)
    else:
        app.logger.error("Failed to fetch coupon information from API")
        return jsonify({"message": "Failed to fetch coupon information."}), 400

#caling the get_events API
@app.route('/get_events')
@login_required
def get_events_route():
    response = requests.get(EVENT_API_URL)
    if response.status_code == 200:
        event_data = response.json()
        return render_template('events.html', event=event_data)
    else:
        return render_template('events.html', event=None)


@app.route('/')
@login_required
def index():
    # Fetch food items from the restaurant menu API
    restaurant_menu = [
        {"id": 1234, "name": "Pepperoni Pizza", "description": "Delicious pizza topped with cheese and pepperoni", "price": 10.99, "image_url": "https://media.istockphoto.com/id/1442417585/photo/person-getting-a-piece-of-cheesy-pepperoni-pizza.jpg?s=612x612&w=0&k=20&c=k60TjxKIOIxJpd4F4yLMVjsniB4W1BpEV4Mi_nb4uJU="},
        {"id": 5678, "name": "Cheese Burger", "description": "A classic American dish consisting of a grilled beef patty topped with cheese, typically served in a bun", "price": 8.99, "image_url": "https://images.immediate.co.uk/production/volatile/sites/2/2020/04/Cheeseburger-74e8cde.jpg?resize=1200%2C630"},
        {"id": 9910, "name": "Caesar Salad", "description": "A classic salad made with romaine lettuce, croutons, Parmesan cheese, and Caesar dressing, originating from Mexico", "price": 6.99, "image_url": "https://t4.ftcdn.net/jpg/02/02/48/35/360_F_202483549_3cDh8uaQ5OJG9GUDsp9YKSQNt69rjucc.jpg"},
        {"id": 1112, "name": "Club Sandwich", "description": "A classic triple-decker sandwich filled with layers of sliced turkey or chicken, bacon, lettuce, tomato, and mayonnaise, served on toasted bread", "price": 9.99, "image_url": "https://www.shutterstock.com/image-photo/four-sandwiches-on-board-600nw-365116274.jpg"},
        {"id": 1314, "name": "Turkey Wrap", "description": "A delicious combination of sliced turkey, fresh vegetables, and savory sauce wrapped in a soft tortilla", "price": 12.99, "image_url": "https://img.freepik.com/free-photo/arabic-shaurma-with-stuffings-lavash_114579-3702.jpg?size=626&ext=jpg&ga=GA1.1.1224184972.1711929600&semt=ais"},
        {"id": 1516, "name": "Lebanese Shawarma", "description": " A savory Middle Eastern dish featuring thinly sliced lamb wrapped in pita bread with garlic sauce, pickles, and sometimes tahini", "price": 7.99, "image_url": "https://t3.ftcdn.net/jpg/03/09/85/36/360_F_309853648_yJJrVCYncv1D4raXzSH39WUlrRMLEwv3.jpg"},
        {"id": 1718, "name": "Chicken Tikka Roll", "description": "A flavorful Indian street food delight featuring grilled chicken tikka wrapped in a soft flatbread, often accompanied by chutneys and fresh vegetables", "price": 11.99, "image_url": "https://thumbs.dreamstime.com/b/chicken-tikka-shawarma-wrap-served-cutting-board-grey-background-side-view-fastfood-chicken-tikka-shawarma-wrap-served-252892440.jpg"},
        {"id": 1920, "name": "Hotdog", "description": "Sausage served in a bun, topped with ketchup, mustard, and onions", "price": 10.99, "image_url": "https://c4.wallpaperflare.com/wallpaper/794/306/483/sausage-fast-food-buns-fast-food-wallpaper-preview.jpg"},
        {"id": 2122, "name": "Taco", "description": "A traditional Mexican dish consisting of a folded or rolled tortilla filled with various ingredients, often including meat, beans, cheese, and vegetables", "price": 12.99, "image_url": "https://images8.alphacoders.com/106/1067917.jpg"},
        {"id": 2324, "name": "Doner Kebab", "description": "A traditional Turkish dish consisting of seasoned meat cooked on a vertical rotisserie, usually served in a pita or flatbread with vegetables and sauce", "price": 13.99, "image_url": "https://media.istockphoto.com/id/1376423897/photo/d%C3%B6ner-kebab-doner-kebap-slice-fast-food-in-flatbread-with-french-fries-on-a-wooden-board.jpg?s=612x612&w=0&k=20&c=5sPfsoWC4lJyKocwyt8eF3OvFwFw51C2k2fX0T5kHo8="},
        {"id": 2526, "name": "Tandoori chicken", "description": "A traditional Indian dish with Chicken marinated in yogurt and spices, then roasted in a tandoor oven", "price": 11.99, "image_url": "https://t3.ftcdn.net/jpg/03/61/02/44/360_F_361024401_whhOCNdEPi0LlQz1lvbyY0dvZuno3aVp.jpg"},
        {"id": 2728, "name": "Chocolate Cookies", "description": "Delicious treats made with cocoa powder and chocolate chips, typically enjoyed as a sweet snack or dessert", "price": 4.99, "image_url": "https://www.shutterstock.com/image-photo/pile-delicious-chocolate-chip-cookies-600nw-1147305941.jpg"}
    ]
    return render_template('index.html', menu=restaurant_menu)

#calling the Allergen API
@app.route('/get_allergen_info', methods=['POST'])
@login_required
def get_allergen_info():
    item_name = request.json['item_name']
    product_id = get_product_id_by_name(item_name)
    if product_id:
        response = requests.get(PRODUCT_ALLERGEN_API_URL, params={'product_id': product_id})
        if response.status_code == 200:
            allergen_info = response.json()
            app.logger.info("API call to PRODUCT_ALLERGEN_API_URL successful")
            return jsonify(allergen_info)
    app.logger.error("Failed to fetch allergen information from API")
    return jsonify({"message": "Allergen information not found for the product"}), 404

def get_product_id_by_name(item_name):
    # Simulate fetching product ID from a database based on item name
    restaurant_menu = [
        {"id": 1234, "name": "Pizza"},
        {"id": 5678, "name": "Burger"},
        {"id": 9910, "name": "Salad"},
        {"id": 1112, "name": "Sandwich"},
        {"id": 1314, "name": "Wrap"},
        {"id": 1516, "name": "Shawarma"},
        {"id": 1718, "name": "Roll"},
        {"id": 1920, "name": "Hotdog"},
        {"id": 2122, "name": "Taco"},
        {"id": 2324, "name": "Kebab"},
        {"id": 2526, "name": "Tandoori"},
        {"id": 2728, "name": "Cookie"}
    ]
    for item in restaurant_menu:
        if item['name'].lower() == item_name.lower():
            return item['id']
    return None

# food item rating function
@app.route('/rate_item', methods=['POST'])
@login_required
def rate_item():
    item_id = request.json['item_id']
    rating = request.json['rating']
    # Update the rating in the database
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute('UPDATE menu_items SET rating = ? WHERE id = ?', (rating, item_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Rating submitted successfully."}), 200


if __name__ == '__main__':
    app.run(debug=True)
