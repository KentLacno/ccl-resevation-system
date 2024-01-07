import os.path
import ast
import json
from flask import (
    Blueprint, redirect, render_template, request,  url_for, jsonify
)
from app.models import Form
from app.models import Respondent
from app.models import Reservation
from app.models import FoodItem
from app.db import db

bp = Blueprint('respondent', __name__, )

@bp.route("/get_respondent/<int:respondentID>")
def get_respondent(respondentID):
  def addFoodItem(reservation):
    reservation["food_item"] = FoodItem.query.get(reservation["food_item_id"]).as_dict()
    return reservation

  respondent = Respondent.query.get(respondentID).as_dict()
  reservations = Reservation.query.filter_by(respondent_id=respondent["id"])
  for weekday in ["monday","tuesday","wednesday","thursday","friday"]:
    filtered_reservations = list(map(lambda x: x.as_dict(), reservations.filter_by(weekday=weekday).all())) 
    reservations_with_food_items = list(map(addFoodItem, filtered_reservations)) 
    print(reservations_with_food_items)
    respondent[weekday] = reservations_with_food_items
  return jsonify(respondent)

@bp.route("/respondent/<int:respondentID>/set_paid", methods=["POST"])
def set_paid(respondentID):
  if request.method == "POST":
    respondent = Respondent.query.get(respondentID)
    respondent.paid = not respondent.paid
    db.session.commit()
  
  return redirect(url_for("form.show", FormID=respondent.form.id))

@bp.route("/respondent/<int:respondentID>/delete", methods=["DELETE"])
def delete(respondentID):
  if request.method == "DELETE":
    respondent = Respondent.query.get(respondentID)
    db.session.delete(respondent)
    db.session.commit()
  
  return redirect(url_for("form.show", FormID=respondent.form.id))