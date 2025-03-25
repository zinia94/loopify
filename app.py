from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
)
import os
import secrets
from database_manager import DatabaseManager
from insert_db_samples import insert_db_samples  # Import DatabaseManager class
from models import UserInfo

# Flask App Setup
app = Flask(__name__)
app.config["SESSION_COOKIE_SECURE"] = True  # Ensure cookies are sent over HTTPS
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(16))

# Initialize Database Manager
db = DatabaseManager()


def get_userinfo_from_session():
    """Helper function to get userinfo from session."""
    return UserInfo(
        session.get("user_id"), session.get("username"), session.get("total_cart_items")
    )


def render_error_page(error_message, errorcode=500, error_template="500.html"):
    """Render an error page with the given error message."""
    session.clear()  # Clear the session to log out the user
    userinfo = get_userinfo_from_session()
    return (
        render_template(error_template, userinfo=userinfo, error_message=error_message),
        errorcode,
    )


@app.route("/")
def home():
    """
    Home route, fetches and displays products for the homepage.
    """
    try:
        userinfo = get_userinfo_from_session()
        response = db.get_all_products(page=1, per_page=4)
        return render_template(
            "index.html", products=response["products"], userinfo=userinfo
        )
    except Exception as e:
        return render_error_page(e)


@app.route("/contact", methods=["GET"])
def contact():
    """
    Displays the contact page with user information.
    """
    userinfo = get_userinfo_from_session()
    return render_template("contact.html", userinfo=userinfo)


@app.route("/product/add", methods=["GET", "POST"])
def add_product():
    """
    Allows users to add a new product, with image upload and category selection.
    """
    userinfo = get_userinfo_from_session()
    if not userinfo.user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        try:
            title = request.form["title"]
            description = request.form["description"]
            price = float(request.form["price"])
            category_id = request.form["category"]
            image = request.files["image"]
            if image:
                image_filename = f"{secrets.token_hex(8)}_{image.filename}"
                image_path = os.path.join("static", "images", image_filename)
                image.save(image_path)
                image_url = f"/static/images/{image_filename}"
            else:
                image_url = "/static/images/no_image.jpg"  # Set to default image if no image is uploaded

            product_id = db.add_product(
                title=title,
                description=description,
                price=price,
                category_id=category_id,
                seller_id=userinfo.user_id,
                image_url=image_url,
            )
            return redirect(url_for("view_product", product_id=product_id))
        except Exception as e:
            render_error_page(e)
    try:
        categories = db.get_all_categories()
        return render_template(
            "add_product.html", categories=categories, userinfo=userinfo
        )
    except Exception as e:
        return render_error_page(e)


@app.route("/product/<int:product_id>")
def view_product(product_id):
    """
    Displays product details and recommended products from the same category.
    """
    try:
        product = db.get_product_by_id(product_id)

        if product is None:
            return render_error_page(
                "Product not found", 404, "404.html"
            )  # Return 404 error if product not found

        userinfo = get_userinfo_from_session()

        added_to_cart = db.is_product_in_cart(userinfo.user_id, product_id)

        all_products_in_category = db.get_products_by_category(product["category_id"])

        # Filter out the current product
        recommended_products = [
            p for p in all_products_in_category if p["id"] != product_id
        ]
        return render_template(
            "view_product.html",
            product=product,
            recommended_products=recommended_products,
            added_to_cart=added_to_cart,
            userinfo=userinfo,
        )

    except Exception as e:

        return render_error_page(e)


@app.route("/search_results", methods=["GET", "POST"])
def search_results():
    """
    Displays search results for products based on search text and selected categories.
    """
    try:
        search_text = request.args.get("q", "").strip()
        selected_categories = request.args.getlist("category[]")

        # Convert selected_categories from strings to integers
        selected_categories = [int(cat_id) for cat_id in selected_categories]

        page = int(request.args.get("page", 1))

        if not search_text:
            search_text = ""
        if not selected_categories:
            selected_categories = []

        result = db.search_products(search_text, selected_categories, page, per_page=9)

        matching_products = result["products"]
        pagination = result["pagination"]

        categories = db.get_all_categories()

        userinfo = get_userinfo_from_session()

        return render_template(
            "search_results.html",
            products=matching_products,
            userinfo=userinfo,
            search_text=search_text,
            selected_categories=selected_categories,
            categories=categories,
            pagination=pagination,
        )
    except Exception as e:
        return render_error_page(e)


@app.route("/cart")
def cart():
    """
    Displays the user's cart with items and total price.
    """
    try:
        userinfo = get_userinfo_from_session()
        cart_items = db.get_cart_items(userinfo.user_id)
        total_price = sum(item["price"] for item in cart_items)
        return render_template(
            "cart.html",
            cart_items=cart_items,
            total_price=total_price,
            userinfo=userinfo,
        )
    except Exception as e:
        return render_error_page(e)


@app.route("/cart/add/<int:product_id>", methods=["GET", "POST"])
def add_to_cart(product_id):
    """
    Adds a product to the cart and redirects to the product's page.
    """
    userinfo = get_userinfo_from_session()
    if not userinfo.user_id:
        return redirect(url_for("login"))

    try:
        added_to_cart = db.is_product_in_cart(userinfo.user_id, product_id)
        if added_to_cart:
            return redirect(url_for("view_product", product_id=product_id))
        db.add_to_cart(userinfo.user_id, product_id)
        session["total_cart_items"] = db.get_total_cart_items(userinfo.user_id)
        return redirect(url_for("view_product", product_id=product_id))
    except Exception as e:
        return render_error_page(e)


@app.route("/cart/remove/<int:product_id>", methods=["POST", "GET"])
def remove_from_cart(product_id):
    """
    Removes a product from the cart and redirects to either cart or product page.
    """
    userinfo = get_userinfo_from_session()
    if not userinfo.user_id:
        return redirect(url_for("login"))

    try:
        if not db.cart_item_exists(
            userinfo.user_id, product_id
        ):  # Check if the cart item exists and belongs to the user
            return render_error_page(
                "Cart item not found or unauthorized access", 404, "404.html"
            )

        db.remove_from_cart(userinfo.user_id, product_id)
        session["total_cart_items"] = db.get_total_cart_items(userinfo.user_id)
        if request.method == "POST":
            return redirect(url_for("cart"))
        else:
            return redirect(url_for("view_product", product_id=product_id))
    except Exception as e:
        return render_error_page(e)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    User login page.
    Handles login form submission and redirects to the homepage on success.
    """
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            user = db.get_user(username, password)
            total_cart_items = db.get_total_cart_items(user["id"])
            if user:
                session["user_id"] = user["id"]
                session["username"] = request.form["username"]
                session["total_cart_items"] = total_cart_items
                return redirect(url_for("home"))
            else:
                flash("Wrong username or password", "error")
        except Exception as e:
            return render_error_page(e)

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    User registration page.
    Allows new users to register and redirects to login on success.
    """
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            db.create_user(username, password)
            return redirect(
                url_for("login")
            )  # Redirect to login page after successful registration
        except Exception as e:
            return render_error_page(e)
    return render_template("register.html")


@app.route("/logout")
def logout():
    """
    Logs out the user and clears session data.
    """
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    try:
        db.create_tables()  # Create necessary tables in the database
        insert_db_samples(
            db
        )  # Insert sample data into the database after creating tables
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    app.run(debug=True)
