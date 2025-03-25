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
                ('Dell Inspiron 15 - Used Laptop, Great Condition', 450.00, 'EUR',
                 'This pre-owned Dell Inspiron 15 laptop is in excellent working condition, perfect for students, professionals, or casual users. Equipped with a powerful processor, ample storage, and a long-lasting battery, it ensures smooth multitasking and efficient performance. The laptop has been well-maintained with minimal signs of wear, making it a budget-friendly alternative to a brand-new device. Whether for work, entertainment, or everyday tasks, this laptop is a reliable choice.', 
                 1, 2, '/static/images/laptop.webp'),
            
                ('Apple iPhone 11 - Gently Used, Unlocked', 350.00, 'EUR',
                 'Upgrade to this pre-owned iPhone 11, fully functional and unlocked for any carrier. This device has been gently used and is in good condition, with a vibrant Liquid Retina HD display, powerful A13 Bionic chip, and excellent battery life. It comes with a high-quality camera system, allowing you to capture stunning photos and 4K videos. Ideal for those looking for a premium smartphone at a fraction of the cost of a new one.', 
                 1, 3, '/static/images/iphone.webp'),
            
                ('Bose QuietComfort 35 - Wireless Noise-Canceling Headphones', 120.00, 'EUR',
                 'Immerse yourself in high-quality sound with these pre-owned Bose QC35 wireless headphones. Featuring world-class noise cancellation, they allow you to focus on your music, work, or calls without distractions. The soft ear cushions ensure all-day comfort, while the long battery life keeps you going for hours. Ideal for travelers, remote workers, or anyone who appreciates premium sound quality at an affordable price.', 
                 2, 2, '/static/images/headphone.webp'),
            
                ('Fitbit Versa - Smart Fitness Watch with Heart Rate Monitor', 80.00, 'EUR',
                 'This used Fitbit Versa smartwatch is perfect for tracking your fitness goals, monitoring heart rate, and staying connected on the go. With built-in activity tracking, sleep monitoring, and smartphone notifications, it’s the ultimate companion for a healthy lifestyle. The watch is in great condition, with a responsive touchscreen, comfortable strap, and long battery life. A budget-friendly way to stay active and organized.', 
                 2, 3, '/static/images/watch.webp'),
            
                ('Men’s Genuine Leather Jacket - Pre-Owned, Stylish & Durable', 60.00, 'EUR',
                 'Upgrade your wardrobe with this classic men’s leather jacket, crafted from genuine leather for a rugged yet stylish look. This pre-owned jacket has been well-kept, offering both warmth and durability. Featuring a comfortable fit and timeless design, it pairs well with casual and semi-formal outfits. Perfect for those who appreciate quality fashion without breaking the bank.', 
                 3, 2, '/static/images/jacket.webp'),
            
                ('Graphic Print Cotton T-Shirt - Casual Wear, Used', 10.00, 'EUR',
                 'This stylish graphic print t-shirt is made from breathable cotton, offering a soft and comfortable fit. Pre-owned but in good condition, it features a modern design that pairs well with jeans, shorts, or joggers. Whether for everyday casual wear or lounging at home, this affordable t-shirt is a great addition to your wardrobe.', 
                 3, 3, '/static/images/tshirt.webp'),
            
                ('Philips High-Speed Blender - Pre-Owned, Works Perfectly', 25.00, 'EUR',
                 'This used Philips blender is in excellent working condition, making it easy to prepare smoothies, shakes, soups, and sauces. With durable stainless steel blades and multiple speed settings, it ensures smooth blending for all your kitchen needs. The compact design fits well on any countertop, and it’s easy to clean after use. An ideal choice for budget-conscious home cooks.', 
                 4, 2, '/static/images/blender.webp'),
            
                ('Nespresso Espresso Coffee Maker - Used, Fully Functional', 50.00, 'EUR',
                 'Enjoy barista-quality coffee at home with this pre-owned Nespresso espresso machine. It’s in great condition and fully functional, delivering rich and aromatic coffee with the press of a button. Compact and stylish, this machine is easy to use and fits perfectly in any kitchen. Ideal for coffee lovers looking for a high-quality machine without the hefty price tag.', 
                 4, 3, '/static/images/coffee_maker.webp'),
            
                ('Python Programming for Beginners - Used Book', 15.00, 'EUR',
                 'This well-maintained book is an excellent introduction to Python programming, perfect for beginners and aspiring developers. Covering fundamental concepts, hands-on exercises, and real-world examples, it helps readers gain confidence in coding. If you’re looking to start a career in tech or improve your programming skills, this affordable used book is a great resource.', 
                 5, 2, '/static/images/python_book.webp'),
            
                ('Data Science Essentials - Second-Hand Book, Like New', 20.00, 'EUR',
                 'Expand your knowledge with this second-hand book on data science basics. Covering key topics such as machine learning, data analysis, and visualization, this book is perfect for students, professionals, and tech enthusiasts. It’s in excellent condition, with no missing pages or major wear. Get high-quality learning material at a lower price.', 
                 5, 3, '/static/images/data_science_book.webp')
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
