import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


class DatabaseManager:
    """A class to manage the SQLite database for the e-commerce application."""

    def __init__(self, db_name="ecommerce.db"):
        self.db_name = db_name

    def connect(self):
        """Establish and return a connection to the database."""
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """Create necessary database tables if they do not already exist."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.executescript(
                """ 
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
            """
            )
            conn.commit()

    def execute_query(
        self, query, params=None, fetch_one=False, fetch_all=False, commit=False
    ):
        """Execute an SQLite query safely and return results if needed."""
        params = params or ()
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                if commit:
                    conn.commit()
        except sqlite3.Error as err:
            raise Exception(f"Database error: {err}")

        return None

    def get_all_products(self, page=1, per_page=5):
        """Retrieve all products from the database with pagination."""
        offset = (page - 1) * per_page
        query_products = """
            SELECT id, title, price, description, image_url 
            FROM products 
            LIMIT ? OFFSET ?
        """
        products = self.execute_query(
            query_products, (per_page, offset), fetch_all=True
        )

        query_count = "SELECT COUNT(*) FROM products"
        total_products = self.execute_query(query_count, fetch_one=True)[0]

        return {
            "products": [
                {
                    "id": p[0],
                    "title": p[1],
                    "price": p[2],
                    "description": p[3],
                    "image_url": p[4],
                }
                for p in products
            ],
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_products": total_products,
                "total_pages": (total_products + per_page - 1) // per_page,
            },
        }

    def search_products(self, search_text, selected_categories, page=1, per_page=8):
        """Search for products by title, description, and category with pagination."""
        offset = (page - 1) * per_page
        query = """
            SELECT p.id, p.title, p.price, p.description, c.name AS category, 
                   p.seller_id, p.image_url, p.category_id
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE (p.title LIKE ? OR p.description LIKE ?)
        """
        params = [f"%{search_text}%", f"%{search_text}%"]
        if selected_categories:
            query += " AND p.category_id IN ({})".format(
                ",".join(["?"] * len(selected_categories))
            )
            params.extend(selected_categories)
        query += " LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        products = self.execute_query(query, params, fetch_all=True)

        count_query = """
            SELECT COUNT(*) FROM products 
            WHERE (title LIKE ? OR description LIKE ?)
        """
        count_params = [f"%{search_text}%", f"%{search_text}%"]
        if selected_categories:
            count_query += " AND category_id IN ({})".format(
                ",".join(["?"] * len(selected_categories))
            )
            count_params.extend(selected_categories)

        total_products = self.execute_query(count_query, count_params, fetch_one=True)[
            0
        ]

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
                    "category_id": p[7],
                }
                for p in products
            ],
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_products": total_products,
                "total_pages": (total_products + per_page - 1) // per_page,
            },
        }

    def get_cart_items(self, user_id):
        """Retrieve all items in a user's cart."""
        query = """
            SELECT cart.id, products.title, products.price, products.image_url, products.id
            FROM cart
            JOIN products ON cart.product_id = products.id
            WHERE cart.user_id = ?
        """
        result = self.execute_query(query, (user_id,), fetch_all=True)

        return [
            {
                "id": item[0],
                "title": item[1],
                "price": item[2],
                "image_url": item[3],
                "product_id": item[4],
            }
            for item in result
        ]

    def is_product_in_cart(self, user_id, product_id):
        """Check if a specific product is in a user's cart."""
        query = "SELECT COUNT(*) FROM cart WHERE user_id = ? AND product_id = ?"
        result = self.execute_query(query, (user_id, product_id), fetch_one=True)
        return result[0] > 0

    def get_products_by_category(self, category_id):
        """Retrieve all products that belong to a specific category."""
        query = """
            SELECT id, title, price, image_url 
            FROM products 
            WHERE category_id = ?
        """
        result = self.execute_query(query, (category_id,), fetch_all=True)

        return [
            {"id": p[0], "title": p[1], "price": p[2], "image_url": p[3]}
            for p in result
        ]

    def add_to_cart(self, user_id, product_id):
        """Add a product to the user's cart."""
        query = "INSERT INTO cart (user_id, product_id) VALUES (?, ?)"
        self.execute_query(query, (user_id, product_id), commit=True)

    def cart_item_exists(self, user_id, product_id):
        """Check if an item already exists in the cart."""
        query = "SELECT COUNT(*) FROM cart WHERE user_id=? AND product_id=?"
        result = self.execute_query(query, (user_id, product_id), fetch_one=True)
        return result[0] > 0

    def remove_from_cart(self, user_id, product_id):
        """Remove a product from the user's cart."""
        query = "DELETE FROM cart WHERE product_id=? AND user_id=?"
        self.execute_query(query, (product_id, user_id), commit=True)

    def create_user(self, username, password):
        """Create a new user with a hashed password."""
        query = "SELECT COUNT(*) FROM users WHERE username=?"
        result = self.execute_query(query, (username,), fetch_one=True)

        if result[0] > 0:
            raise ValueError("Username already exists.")

        hashed_password = generate_password_hash(password)
        query = "INSERT INTO users (username, password) VALUES (?, ?)"
        self.execute_query(query, (username, hashed_password), commit=True)

    def get_user(self, username, password):
        """Retrieve a user by username and verify the password."""
        query = "SELECT id, password FROM users WHERE username=?"
        user = self.execute_query(query, (username,), fetch_one=True)

        if user and check_password_hash(user[1], password):
            return {"id": user[0]}
        return None
    
    def add_product(
        self, title, price, description, category_id, seller_id, image_url=None
    ):
        """
        Add a new product to the database with the given details.
        """
        query = """
            INSERT INTO products (title, price, description, category_id, seller_id, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        result = self.execute_query(
            query,
            (title, price, description, category_id, seller_id, image_url),
            commit=True,
        )
        return result.lastrowid

    def get_all_categories(self):
        """
        Retrieve all categories from the database.
        """
        query = "SELECT id, name FROM categories"
        categories = self.execute_query(query, fetch_all=True)
        return [{"id": c[0], "name": c[1]} for c in categories]

    def get_product_by_id(self, product_id):
        """
        Fetch details of a specific product by its ID.
        """
        query = """
            SELECT p.id, p.title, p.price, p.description, c.name AS category, p.seller_id, p.image_url, p.category_id
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
        """
        product = self.execute_query(query, (product_id,), fetch_one=True)

        if product is None:
            return None

        return {
            "id": product[0],
            "title": product[1],
            "price": product[2],
            "description": product[3],
            "category": product[4],
            "seller_id": product[5],
            "image_url": product[6],
            "category_id": product[7],
        }

    def get_total_cart_items(self, user_id):
        """
        Get the total number of items in a user's cart.
        """
        query = "SELECT COUNT(*) FROM cart WHERE user_id = ?"
        result = self.execute_query(query, (user_id,), fetch_one=True)
        return result[0] if result[0] is not None else 0
