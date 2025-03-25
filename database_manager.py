import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class DatabaseManager:
    
    """A class to manage the SQLite database for the e-commerce application."""
    def __init__(self, db_name='ecommerce.db'):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """
        Create the necessary database tables if they do not already exist.
        This method establishes a connection to the database and creates the following tables:
        - `users`: Stores user information, including a unique username and password.
        - `categories`: Stores product category information with unique names.
        - `products`: Stores product details, including title, price, stock quantity, description, 
          category, seller, and an optional image URL. It has foreign key relationships with 
          `categories` and `users` tables.
        - `cart`: Stores information about products added to a user's cart, with foreign key 
          relationships to the `users` and `products` tables.
        All tables are created only if they do not already exist in the database.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL);
                
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL);
                
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'EUR',
                    description TEXT,
                    category_id INTEGER NOT NULL,
                    seller_id INTEGER NOT NULL,
                    image_url TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories (id),
                    FOREIGN KEY (seller_id) REFERENCES users (id));
                
                CREATE TABLE IF NOT EXISTS cart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL);
            ''')
            conn.commit()

    def get_all_products(self, page=1, per_page=5):
        """
        Retrieve all products from the database with pagination.
        Args:
            page (int): The page number to retrieve.
            per_page (int): The number of products per page.
        Returns:
            dict: A dictionary containing the products and pagination metadata.
        """
        offset = (page - 1) * per_page
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, price, description, image_url 
                FROM products 
                LIMIT ? OFFSET ?
            ''', (per_page, offset))
            products = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]

        return {
            "products": [
                {
                    "id": p[0],
                    "title": p[1],
                    "price": p[2],
                    "description": p[3],
                    "image_url": p[4]
                } for p in products
            ],
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_products": total_products,
                "total_pages": (total_products + per_page - 1) // per_page
            }
        }

    def search_products(self, search_text, selected_categories, page=1, per_page=8):
        """
        Search for products by title, description, and category, with pagination.

        Args:
            search_text (str): The text to search in product title and description.
            selected_categories (list): A list of category IDs to filter by.
            page (int): The page number.
            per_page (int): The number of products per page.

        Returns:
            dict: A dictionary containing the products and pagination metadata.
        """
        offset = (page - 1) * per_page
        query = '''SELECT p.id, p.title, p.price, p.description, c.name AS category, p.seller_id, p.image_url, p.category_id
                   FROM products p
                   JOIN categories c ON p.category_id = c.id
                   WHERE (p.title LIKE ? OR p.description LIKE ?)'''

        params = [f'%{search_text}%', f'%{search_text}%']

        if selected_categories:
            query += " AND p.category_id IN ({})".format(','.join(['?'] * len(selected_categories)))
            params.extend(selected_categories)

        query += " LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            products = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM products WHERE (title LIKE ? OR description LIKE ?)", (f'%{search_text}%', f'%{search_text}%'))
            total_products = cursor.fetchone()[0]

            if selected_categories:
                cursor.execute(
                    "SELECT COUNT(*) FROM products WHERE (title LIKE ? OR description LIKE ?) AND category_id IN ({})".format(
                        ','.join(['?'] * len(selected_categories))
                    ),
                    [f'%{search_text}%', f'%{search_text}%'] + selected_categories
                )
                total_products = cursor.fetchone()[0]

        return {
            "products": [
                {
                    "id": p[0],
                    "title": p[1],
                    "price": p[2],
                    "description": p[3],
                    "category": p[4],
                    "seller_id": p[5],
                    "image_url": p[6],
                    "category_id": p[7]
                } for p in products
            ],
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_products": total_products,
                "total_pages": (total_products + per_page - 1) // per_page
            }
        }


    def get_recommendations(self, product_id):
        """Get recommended products based on the same category."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category_id FROM products WHERE id=?", (product_id,))
            category = cursor.fetchone()

            if category:
                cursor.execute("SELECT id, title, price, image_url FROM products WHERE category_id=? AND id!=?", (category[0], product_id))
                recommendations = cursor.fetchall()
            else:
                recommendations = []

        return [{'id': p[0], 'title': p[1], 'price': p[2], 'image_url': p[3]} for p in recommendations]

    def get_cart_items(self, user_id):
        """Retrieve all items in the cart for a specific user."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cart.id, products.title, products.price, products.image_url ,products.id
                FROM cart 
                JOIN products ON cart.product_id = products.id
                WHERE cart.user_id = ?
            ''', (user_id,))
            cart_items = cursor.fetchall()
        return [{'id': item[0], 'title': item[1], 'price': item[2], 'image_url': item[3], 'product_id': item[4]} for item in cart_items]
    
    def get_products_by_category(self, category_id):
        """Get all products by category."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, price, image_url 
                FROM products 
                WHERE category_id = ?
            ''', (category_id,))
            products = cursor.fetchall()

        return [{'id': p[0], 'title': p[1], 'price': p[2], 'image_url': p[3]} for p in products]


    def add_to_cart(self, user_id, product_id):
        """Add a product to the cart."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cart (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
            conn.commit()
            
    def cart_item_exists(self, user_id, product_id):
        """Check if a product is already in the cart for a specific user."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))
            count = cursor.fetchone()[0]
        return count > 0
    
    def remove_from_cart(self, user_id, product_id):
        """Remove a product from the cart if it belongs to the user."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE product_id=? AND user_id=?", (product_id, user_id))
            conn.commit()

    def create_user(self, username, password):
        """Insert a new user with hashed password if the username does not already exist."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username=?", (username,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Username already exists.")
            
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()

    def get_user(self, username, password):
        """Retrieve user details and validate password securely."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

        if user and check_password_hash(user[1], password):
            return {"id": user[0]}
        return None
    
    def add_product(self, title, price, description, category_id, seller_id, image_url=None):
        """
        Add a new product to the database and return its ID.
        Args:
            title (str): The title of the product.
            price (float): The price of the product.
            description (str): The description of the product.
            category_id (int): The ID of the category the product belongs to.
            seller_id (int): The ID of the seller adding the product.
            image_url (str, optional): The URL of the product image.
        Returns:
            int: The ID of the newly added product.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (title, price, description, category_id, seller_id, image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, price, description, category_id, seller_id, image_url))
            conn.commit()
            return cursor.lastrowid
            
    def get_all_categories(self):
        """
        Retrieve all categories from the database.
        Returns:
            list: A list of dictionaries containing category details.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories")
            categories = cursor.fetchall()
        return [{"id": c[0], "name": c[1]} for c in categories]

    def get_product_by_id(self, product_id):
        """
        Retrieve a product by its ID, including the category name instead of the category ID.
        Args:
            product_id (int): The ID of the product to retrieve.
        Returns:
            dict: A dictionary containing the product details, or None if the product does not exist.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.title, p.price,  p.description, c.name AS category, p.seller_id, p.image_url, p.category_id
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.id = ?
            ''', (product_id,))
            product = cursor.fetchone()

        if product:
            return {
                "id": product[0],
                "title": product[1],
                "price": product[2],
                "description": product[3],
                "category": product[4],
                "seller_id": product[5],
                "image_url": product[6],
                "category_id": product[7]
            }
        return None