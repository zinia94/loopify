from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    url_for,
    redirect,
    flash,
)
from app.utils import get_userinfo_from_session, render_error_page, save_image
from flask_login import login_required
import logging

product_bp = Blueprint("product", __name__)


@product_bp.route("/<int:product_id>")
def view_product(product_id):
    """
    Displays product details and recommended products from the same category.
    """
    try:
        db = current_app.db
        product = db.get_product_by_id(product_id)
        if not product:
            return render_error_page("Product not found", 404)

        userinfo = get_userinfo_from_session()
        added_to_cart = db.cart_item_exists(userinfo.user_id, product_id)

        recommended_products = [
            p
            for p in db.get_products_by_category(product.category_id)
            if p.id != product_id
        ]
        return render_template(
            "view_product.html",
            product=product,
            recommended_products=recommended_products,
            added_to_cart=added_to_cart,
            userinfo=userinfo,
        )
    except Exception as e:
        logging.error(e)
        return render_error_page(e)


@product_bp.route("/add", methods=["POST", "GET"])
@login_required
def add_product():
    """
    Allows users to add a new product, with image upload and category selection.
    """
    db = current_app.db
    userinfo = get_userinfo_from_session()

    if request.method == "POST":
        try:
            title = request.form["title"]
            description = request.form["description"]
            price = float(request.form["price"])
            category_id = request.form["category"]
            image = request.files["image"]

            image_url = save_image(image)

            product = db.add_product(
                title=title,
                description=description,
                price=price,
                category_id=category_id,
                seller_id=userinfo.user_id,
                image_url=image_url,
            )
            return redirect(url_for("product.view_product", product_id=product.id))
        except Exception as e:
            logging.error(e)
            return render_error_page(e)
    try:
        categories = db.get_all_categories()
        logging.debug(categories)
        return render_template(
            "manage_product.html",
            categories=categories,
            userinfo=userinfo,
            product=None,
        )
    except Exception as e:
        return render_error_page(e)


@product_bp.route("/update/<int:product_id>", methods=["POST", "GET"])
@login_required
def update_product(product_id):
    """
    Allows users to update a product. Only the seller can update the product.
    """
    db = current_app.db
    userinfo = get_userinfo_from_session()

    product = db.get_product_by_id(product_id)

    if product.seller_id != userinfo.user_id:
        return render_error_page("Unauthorized access", 403)

    if request.method == "POST":
        try:
            title = request.form["title"]
            description = request.form["description"]
            price = float(request.form["price"])
            category_id = request.form["category"]
            image = request.files["image"]

            image_url = save_image(image) if image else product.image_url

            db.update_product(
                product_id=product.id,
                title=title,
                description=description,
                price=price,
                category_id=category_id,
                image_url=image_url,
            )

            return redirect(url_for("product.view_product", product_id=product.id))
        except Exception as e:
            logging.error(e)
            return render_error_page(e)

    categories = db.get_all_categories()
    return render_template(
        "manage_product.html", product=product, categories=categories, userinfo=userinfo
    )


@product_bp.route("/delete/<int:product_id>", methods=["GET"])
@login_required
def delete_product(product_id):
    """
    Deletes a product if the logged-in user is the seller.
    """
    db = current_app.db
    userinfo = get_userinfo_from_session()

    product = db.get_product_by_id(product_id)

    if not product:
        return render_error_page("Product not found.", 404)

    if product.seller_id != userinfo.user_id:
        return render_error_page("Unauthorized access", 403)

    try:
        db.delete_product(product_id)
        flash("Product deleted successfully.", "success")
        return redirect(
            url_for("general.home")
        )  # Redirect to home or product listing page
    except Exception as e:
        logging.error(f"Error deleting product: {e}")
        return render_error_page("There was an error deleting the product.")


@product_bp.route("/search_results")
def search_results():
    """
    Displays search results for products based on search text and selected categories.
    """
    try:
        db = current_app.db
        search_text = request.args.get("q", "").strip()
        selected_categories = request.args.getlist("category[]")
        selected_categories = [int(cat) for cat in selected_categories if cat.isdigit()]
        page = int(request.args.get("page", 1))

        result = db.search_products(search_text, selected_categories, page, per_page=9)
        userinfo = get_userinfo_from_session()
        categories = db.get_all_categories()

        return render_template(
            "search_results.html",
            products=result["products"],
            pagination=result["pagination"],
            userinfo=userinfo,
            categories=categories,
            search_text=search_text,
            selected_categories=selected_categories,
        )
    except Exception as e:
        logging.error(e)
        return render_error_page(e)


@product_bp.route("/my-products", methods=["GET"])
@login_required
def my_products():
    """
    List all products created by the logged-in user.
    """
    try:
        db = current_app.db
        products = db.get_products_by_seller_id(current_user.id)
        return render_template("my_products.html", products=products)
    except Exception as e:
        flash(f"Error loading products: {e}", "danger")
        return redirect(url_for("general.home"))
