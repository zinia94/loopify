from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os
import secrets
from database_manager import DatabaseManager
from insert_db_samples import insert_db_samples  # Import DatabaseManager class

# Flask App Setup
app = Flask(__name__)
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are sent over HTTPS
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Initialize Database Manager
db = DatabaseManager()

class UserInfo:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

def get_userinfo_from_session():
    """Helper function to get userinfo from session."""
    return UserInfo(session.get('user_id'), session.get('username'))

@app.route('/')
def home():
    try:
        userinfo = get_userinfo_from_session()  # Use helper function
        response = db.get_all_products(page=1, per_page= 4)
        return render_template('index.html', products=response["products"], userinfo=userinfo)
    except Exception as e:
        return jsonify({'error': str(e)})

    
@app.route('/contact', methods=['GET'])
def contact():
    userinfo = get_userinfo_from_session()  # Use helper function
    return render_template('contact.html', userinfo=userinfo)

@app.route('/product/add', methods=['GET', 'POST'])
def add_product():
    userinfo = get_userinfo_from_session()  # Use helper function
    if not userinfo.user_id:
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            price = float(request.form['price'])
            category_id = request.form['category']
            image = request.files['image']  # Get the uploaded image file
            if image:
                # Create a unique filename for the image
                image_filename = f"{secrets.token_hex(8)}_{image.filename}"
                image_path = os.path.join('static', 'images', image_filename)
                # Save the image to the static/images folder
                image.save(image_path)
                # Create the image URL to save in the database
                image_url = f"/static/images/{image_filename}"
            else:
                image_url = "/static/images/no_image.jpg"  # Set to None if no image is uploaded
            
            # Add the new product to the database with seller_id as user_id
            product_id = db.add_product(title=title, description=description, price=price, category_id=category_id, seller_id=userinfo.user_id, image_url=image_url)
            return redirect(url_for('view_product', product_id=product_id))  # Redirect to product page after adding the product
        except Exception as e:
            return jsonify({'error': str(e)})
    try:
        categories = db.get_all_categories()  # Fetch all categories from the database
        return render_template('add_product.html', categories=categories, userinfo = userinfo)  # Pass categories to the template
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/product/<int:product_id>')
def view_product(product_id):
    try:
        product = db.get_product_by_id(product_id)  # Fetch product details by ID
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Fetch all products from the same category
        all_products_in_category = db.get_products_by_category(product['category_id'])
    
        # Filter out the current product
        recommended_products = [
            p for p in all_products_in_category if p['id'] != product_id
        ]

        userinfo = get_userinfo_from_session()  # Use helper function
        return render_template('view_product.html', product=product, recommended_products=recommended_products, userinfo=userinfo)

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    try:
        # Get search text from the query parameter 'q'
        search_text = request.args.get('q', '').strip()
        
        # Get selected categories from the query parameter 'category'
        selected_categories = request.args.getlist('category[]')
        
        
        # Convert selected_categories from strings to integers
        selected_categories = [int(cat_id) for cat_id in selected_categories]
        
        # Get current page (default to 1 if not specified)
        page = int(request.args.get('page', 1))

        # If no search text or categories, redirect to home
        if not search_text:
            search_text = ''
        if not selected_categories:
            selected_categories = []
       
        # Search for products with pagination
        result = db.search_products(search_text, selected_categories, page, per_page=9)
        
        matching_products = result['products']
        pagination = result['pagination']
        
        # Fetch all categories from the database for displaying in the filter
        categories = db.get_all_categories()

        # Get user ID from session for potential use (e.g., adding products to cart)
        userinfo = get_userinfo_from_session()

        # Render the search results template, passing the products, categories, and selected categories
        return render_template('search_results.html', 
                               products=matching_products, 
                               userinfo=userinfo, 
                               search_text=search_text, 
                               selected_categories=selected_categories,
                               categories=categories,
                               pagination=pagination)
    except Exception as e:
        return jsonify({'error': str(e)})




@app.route('/cart')
def cart():
    try:
        userinfo = get_userinfo_from_session()  # Use helper function
        cart_items = db.get_cart_items(userinfo.user_id)  # Fetch cart items for the user
        total_price = sum(item['price'] for item in cart_items)  # Calculate total price
        return render_template('cart.html', cart_items=cart_items, total_price=total_price, userinfo=userinfo)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/cart/add/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    userinfo = get_userinfo_from_session()  # Use helper function
    if not userinfo.user_id:
        return redirect(url_for('login'))  # Redirect to login page if not logged in

    try:
        db.add_to_cart(userinfo.user_id, product_id)
        return redirect(url_for('cart'))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    userinfo = get_userinfo_from_session()  # Use helper function
    if not userinfo.user_id:
        return redirect(url_for('login'))  # Redirect to login page if not logged in

    try:
        if not db.cart_item_exists(userinfo.user_id, product_id):  # Check if the cart item exists and belongs to the user
            return jsonify({'error': 'Cart item not found or unauthorized access'}), 404

        db.remove_from_cart(userinfo.user_id, product_id)
        return redirect(url_for('cart'))
    except Exception as e:
        return jsonify({'error': str(e)})  # Return error message in case of an exception

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            user = db.get_user(username, password)
            if user:
                session['user_id'] = user['id']  # Store user ID in session
                session['username'] = request.form['username']
                return redirect(url_for('home'))  # Redirect to homepage
            else:
                flash('Wrong username or password', 'error')
        except Exception as e:
            return jsonify({'error': str(e)})

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            db.create_user(username, password)  # Create a new user in the database
            return redirect(url_for('login'))  # Redirect to login page after successful registration
        except Exception as e:
            return jsonify({'error': str(e)})
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    # removes the user from the session.
    return redirect(url_for('home'))

if __name__ == '__main__':
    try:
        # Create necessary tables in the database
        db.create_tables()
        # Insert sample data into the database after creating tables
        insert_db_samples(db)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    app.run(debug=True)
