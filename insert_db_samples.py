from werkzeug.security import generate_password_hash
        
def insert_test_users_with_hashed_passwords(db):
    """Insert at least 3 test users with hashed passwords if they do not already exist."""
    with db.connect() as conn:
        cursor = conn.cursor()
        users = [
            ('testuser1', generate_password_hash('password1')),
            ('testuser2', generate_password_hash('password2')),
            ('testuser3', generate_password_hash('password3'))
        ]
        cursor.executemany("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", users)
        conn.commit()

def insert_categories(db):
    """Insert predefined categories if they do not already exist."""
    with db.connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        if count == 0:
            categories = [
                ('Electronics',),
                ('Accessories',),
                ('Clothing',),
                ('Home & Kitchen',),
                ('Books',),
                ('Toys',),
                ('Sports',),
                ('Beauty & Personal Care',)
            ]
            cursor.executemany("INSERT INTO categories (name) VALUES (?)", categories)
            conn.commit()
            
def insert_sample_products_with_seller(db):
    """Insert a list of sample used products into the database with seller_id always 2 or 3."""
    with db.connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        if count == 0:
            products = [
                ('Used Laptop - Dell Inspiron', 450.00, 'EUR', 5, 'A well-maintained used Dell Inspiron laptop.', 1, 2, '/static/images/laptop.webp'),
                ('Used Smartphone - iPhone 11', 350.00, 'EUR', 3, 'A used iPhone 11 in good condition.', 1, 3, '/static/images/iphone.webp'),
                ('Used Headphones - Bose QC35', 120.00, 'EUR', 7, 'Noise-cancelling Bose QC35 headphones.', 2, 2, '/static/images/headphone.webp'),
                ('Used Smartwatch - Fitbit Versa', 80.00, 'EUR', 10, 'A used Fitbit Versa smartwatch.', 2, 3, '/static/images/watch.webp'),
                ('Used Jacket - Leather', 60.00, 'EUR', 4, 'A stylish used leather jacket.', 3, 2, '/static/images/jacket.webp'),
                ('Used T-shirt - Graphic Print', 10.00, 'EUR', 15, 'A used graphic print t-shirt.', 3, 3, '/static/images/laptop.webp'),
                ('Used Blender - Philips', 25.00, 'EUR', 8, 'A used Philips blender in working condition.', 4, 2, '/static/images/laptop.webp'),
                ('Used Coffee Maker - Nespresso', 50.00, 'EUR', 6, 'A used Nespresso coffee maker.', 4, 3, '/static/images/laptop.webp'),
                ('Used Book - Python Programming', 15.00, 'EUR', 12, 'A used book on Python programming.', 5, 2, '/static/images/laptop.webp'),
                ('Used Book - Data Science Basics', 20.00, 'EUR', 10, 'A used book on data science basics.', 5, 3, '/static/images/laptop.webp')
            ]
            cursor.executemany('''INSERT INTO products 
                                   (title, price, currency, description, category_id, seller_id, image_url) 
                                   VALUES (?, ?, ?, ?, ?, ?, ?)''', products)
            conn.commit()
            
def insert_db_samples(db):
    try:
        insert_test_users_with_hashed_passwords(db)
        insert_categories(db)
        insert_sample_products_with_seller(db)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
