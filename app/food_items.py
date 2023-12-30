import os.path
import ast
from flask import (
    Blueprint, redirect, render_template, request,  url_for
)
from app.models import FoodItem
from app.db import db

bp = Blueprint('food_items', __name__, )

@bp.route("/food_items", methods=["POST", "GET"])
def index():
  alert = request.args.get('alert')
  food_items = FoodItem.query.all()
  if request.method == "POST":
    print(request.form)
    form = request.form
    add_food_item = FoodItem(
        name=form["name"],
        price=form["price"],
        image=form["image_url"]
    )
    print(add_food_item)
    db.session.add(add_food_item)
    db.session.commit()

    return redirect(url_for('food_items.index'))
  else:
    return render_template('food_items.html', food_items=food_items, alert=alert, len=len)
  
@bp.route('/food_items/<int:id>/update', methods=['POST'])
def update(id):

    form = request.form
    food_item = FoodItem.query.get(id)
    food_item.name = form["name"]
    food_item.price = form["price"]
    food_item.image = form["image_url"]

    db.session.commit()
    return redirect(url_for('food_items.index'))

@bp.route('/food_items/<int:id>/delete', methods=['POST'])
def delete(id):
    food_item = FoodItem.query.get(id)
    db.session.delete(food_item)
    db.session.commit()
    return redirect(url_for('food_items.index', alert="delete_success"))