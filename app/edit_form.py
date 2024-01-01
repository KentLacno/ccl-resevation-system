import os.path
import ast
import json

from flask import (
    Blueprint, redirect, render_template, request,  url_for
)

from app.db import db

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
from datetime import timedelta
from app.models import Form
from app.models import FoodItem
from app.models import Options
from food_items import *

bp = Blueprint('edit_form', __name__, )

SCOPES = ["https://www.googleapis.com/auth/forms.body"]

def build_form_service():
  creds = None
  if os.path.exists("form_token.json"):
    try:
      creds = Credentials.from_authorized_user_file("form_token.json", SCOPES)
    except:
      if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
        else:
          flow = InstalledAppFlow.from_client_secrets_file(
              "credentials.json", SCOPES
          )
          creds = flow.run_local_server(port=0)
        with open("form_token.json", "w") as token:
          token.write(creds.to_json())

  form_service = build("forms", "v1", credentials=creds)
  return form_service

def parse_body(form, google_form): 
  weekdays = [
    {"weekday":"monday","index": 2},
    {"weekday":"tuesday","index": 3},
    {"weekday":"wednesday","index": 4},
    {"weekday":"thursday","index": 5},
    {"weekday":"friday","index": 6}
  ]


  def format_option(item):
    item = FoodItem.query.get(item)
    return {"value": "({id}) {name} - ₱{price}".format(id=item.id, name=item.name, price=item.price), "image": {"sourceUri": item.image}}
    
  def convert_item(weekday_data):
    weekday = weekday_data["weekday"]
    item = {}
    if form.getlist(weekday):
      form_item = [x for x in google_form['items'] if "title" in x and x["title"]  == weekday.capitalize()]
      if len(form_item) == 0:
        item = {
            "updateItem": {
              "item": {
                "itemId": form_item["itemId"],
                "questionItem": {
                  "question": {
                    "choiceQuestion": {
                      "type": "CHECKBOX",
                      "options": list(map(format_option, form.getlist(weekday))),
                    },
                  }
                },
              },
              "location": {"index": weekday_data["index"]},
              "updateMask": ""
            }
          }
      return item
    return 
    
  update = {"requests": list(map(convert_item, weekdays))}
  print(update)
  return update

@bp.route("/edit_form/<int:FormID>", methods=["POST", "GET"])
def edit_form(FormID):
  form = Form.query.get(FormID)
  if request.method == "POST":
      form_response = request.form
      form_service = build_form_service()
 
      get_result = form_service.forms().get(formId=form.form_id).execute()
      (
          form_service.forms()
          .batchUpdate(formId=form.form_id, body=parse_body(form_response, get_result))
          .execute()
      )

      Options.query.filter_by(form=form).delete()
      
      for weekday in ["monday","tuesday","wednesday","thursday","friday"]:
        if form_response.getlist(weekday):
          for item in form_response.getlist(weekday):
            add_options = Options(
              form=form,
              food_item=FoodItem.query.get(item),
              weekday=weekday
            )
            db.session.add(add_options)

      db.session.commit()
      return redirect(url_for('form.show',FormID=form.id))
  else:
    food_items = FoodItem.query.all()
    
    return render_template('edit_form.html', form=form, food_items=food_items)

@bp.route("/test", methods=["POST", "GET"])
def test():
    food_items = FoodItem.query.all()
    print(FOOD_ITEMS)
    return "ahh"
