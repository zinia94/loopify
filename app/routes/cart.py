from flask import (
    Blueprint,
    redirect,
    url_for,
    session,
    current_app,
    render_template,
    request,
)
from app.utils import get_userinfo_from_session, render_error_page
from flask_login import login_required
import logging

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/")
def cart():
    """
    Displays the user's cart with items and total price.
    """
    try:
        db = current_app.db
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
        logging.error(e)
        return render_error_page(e)


@cart_bp.route("/add/<int:product_id>", methods=["GET", "POST"])
@login_required
def add_to_cart(product_id):
    """
    Adds a product to the cart and redirects to the product's page.
    """
    userinfo = get_userinfo_from_session()
    try:
        db = current_app.db
        added_to_cart = db.cart_item_exists(userinfo.user_id, product_id)
        if added_to_cart:
            return redirect(url_for("product.view_product", product_id=product_id))
        
        product = db.get_product_by_id(product_id)
        if not product:
            return render_error_page("Product not found", 404)
        
        if product.seller_id != userinfo.user_id :
            db.add_to_cart(userinfo.user_id, product_id)
            session["total_cart_items"] = db.get_total_cart_items(userinfo.user_id)
        
        return redirect(url_for("product.view_product", product_id=product_id))
    except Exception as e:
        return render_error_page(e)


@cart_bp.route("/remove/<int:product_id>", methods=["POST", "GET"])
@login_required
def remove_from_cart(product_id):
    """
    Removes a product from the cart and redirects to either cart or product page.
    """
    userinfo = get_userinfo_from_session()

    try:
        db = current_app.db
        if not db.cart_item_exists(
            userinfo.user_id, product_id
        ):  # Check if the cart item exists and belongs to the user
            return render_error_page("Cart item not found or unauthorized access", 404)

        db.remove_from_cart(userinfo.user_id, product_id)
        session["total_cart_items"] = db.get_total_cart_items(userinfo.user_id)
        if request.method == "POST":
            return redirect(url_for("cart.cart"))
        else:
            return redirect(url_for("product.view_product", product_id=product_id))
    except Exception as e:
        return render_error_page(e)
