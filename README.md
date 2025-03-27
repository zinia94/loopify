# Loopify - Sustainable Marketplace

Loopify is an online marketplace designed to help users buy and sell used items, promoting sustainability through the reuse and recycling of goods. The platform is built with Flask for the backend, SQLite for the database, and HTML, CSS, and JavaScript for the frontend. It allows users to manage product listings, add products to their shopping cart, and explore product recommendations.

## Features
- **Product Listings:** Browse available products for sale.
- **Add to Cart:** Add products to the cart and manage selections.
- **Product Management:** Sellers can add, update, or delete their products.
- **Search Functionality:** Search products based on title and description.
- **Category Filtering:** Filter products by category for easier browsing.
- **Product Recommendation System:** Get recommendations for similar products within the same category.
- **User Login/Registration:** Users can create an account or log in to manage their cart and product listings.

**The checkout process is out of scope for this project.*

## Tech Stack
- **Flask:** Lightweight Python web framework for building the backend.
- **Flask-Login:** User authentication and session management.
- **SQLAlchemy:** Object-Relational Mapping (ORM) to interact with the SQLite database.
- **SQLite:** Serverless, self-contained database to store user, product, and cart information.
- **pytest:** Testing framework for backend functionality.
- **HTML/CSS:** Core technologies for building the frontend.
- **JavaScript:** Enhances interactivity for frontend elements.
- **Black Formatter:** Python code formatter for maintaining PEP 8 code standards.

## Setup and Installation

### Prerequisites
- Python 3.x
- Virtual environment tool (`venv`)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/loopify.git
cd loopify
```

### 2. Set up the virtual environment

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```
**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```
### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

Start the Flask development server:

```bash
python run.py
```
The app will be running at http://127.0.0.1:5000/ by default.

### Running Tests

To run the tests, use pytest:
```bash
pytest
```

## Database Design

The Loopify application uses an SQLite database to store persistent data. The schema includes the following main tables:

1. **User Table:** Stores user information such as username, password hash, and active status.

2. **Product Table:** Stores product details such as title, price, description, and seller information.

3. **Category Table:** Stores product categories like Electronics, Clothing, etc.

4. **Cart Table:** Stores items added to a user's cart.

### Table Relationships

- **User-Product Relationship:** One user can have multiple products, but each product belongs to one seller (user).

- **Product-Category Relationship:** One category can have many products, but each product belongs to only one category.

- **User-Cart Relationship:** One user can have multiple products in their cart, but each cart item is associated with one user and one product.

### Indexes

- **User Table:** Indexed on `username.`

- **Product Table:** Indexed on `title` and `category_id.`

- **Cart Table:** Indexed on `user_id` and `product_id.`

## Frontend Design

The frontend is designed to be responsive and user-friendly, ensuring a seamless experience across desktops, tablets, and mobiles. Key frontend pages include:

- **Landing Page:** Displays featured products.

- **Product Listing Page:** Displays a list of products with search and filter options.

- **Product Detail Page:** Shows detailed information about products, including similar recommendations.

- **Cart Page:** Displays items in the user's cart.

- **Login/Registration Pages:** Allow users to create an account or log in.

- **Product Management Pages:** Allows sellers to add, edit, or delete their products.

### Technologies Used

- `HTML` for page structure.

- `CSS` for styling and responsiveness.

- `JavaScript` for interactive frontend features like dropdown menus and form validation.

## Backend Design

The backend is built using Flask and handles core functionalities such as:

- **Authentication and Authorization:** Manages user login, registration, and session management.

- **Product Management:** CRUD operations for adding, updating, and deleting products.

- **Cart Management:** Allows users to add and remove products from their shopping cart.

- **Search and Filtering:** Supports searching for products by title and filtering by category.

### Database Operations

- **SQLAlchemy ORM** is used to interact with the database. Key models include `User`, `Product`, `Category`, and `Cart`.

- **Helper Functions:** Various functions like `get_product_by_id`, `get_cart_items`, and `get_all_products` are used to retrieve data from the database.

## Testing

The application includes unit tests for ensuring the functionality of core features. Tests are organized in the `tests` folder, and `pytest` is used to run the tests.

```bash
pytest
```

## Future Enhancements

- **Checkout and Payment System:** Implement a checkout process with payment gateway integration.

- **User Ratings and Reviews:** Allow users to rate and review products.

- **Product Search Enhancements:** Improve search algorithms for better product discovery.