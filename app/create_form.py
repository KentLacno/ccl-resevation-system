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

bp = Blueprint('create_form', __name__, )

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

def parse_date(week_data):
    year = int(week_data.split("-")[0])
    week = int(week_data.split("W")[-1])
    
    start_date = datetime.date.fromisocalendar(year,week,1)
    end_date = start_date + timedelta(days=7)

    parsed_date = start_date.strftime("%b %d, %Y") + " - " + end_date.strftime("%b %d %Y")
    return parsed_date

def parse_body(form): 
  weekdays = ["friday", "thursday", "wednesday", "tuesday", "monday"]
  print(form)

  def format_option(item):
    item = FoodItem.query.get(item)
 
    return {"value": "({id}) {name} - ₱{price}".format(id=item.id, name=item.name, price=item.price), "image": {"sourceUri": item.image}}
  
  def convert_item(weekday):
    if form.getlist(weekday):
      print(form.getlist(weekday)[0])
      item = {
          "createItem": {
            "item": {
              "title": (weekday.capitalize()),
              "questionItem": {
                "question": {
                  "choiceQuestion": {
                    "type": "CHECKBOX",
                    "options": list(map(format_option, form.getlist(weekday))),
                  },
                }
              },
            },
            "location": {"index": 0},
          }
        }
      return item
    return 
    
  update = {
  "requests": list(map(convert_item, weekdays)) +
    [{
        "createItem": {
          "item": {
            "title": "Grade and Section",
            "questionItem": {
                "question": {
                  "choiceQuestion": {
                    "type": "DROP_DOWN",
                    "options": [
                      {"value": "7-ambot"},
                      {"value": "8-ambot"},
                      {"value": "9-ambot"},
                      {"value": "10-Benevolence"},
                      {"value": "10-Prudence"},
                      {"value": "11-Frugality"},
                      {"value": "12-Resilience"},
                    ],
                  },
                }
              },
          },
          "location": {"index": 0}
        }
      },
      {
        "createItem": {
          "item": {
            "title": "Name",
            "questionItem": {
              "question": {
                "textQuestion": {
                  "paragraph": False,
                },
              }
            },
          },
          "location": {"index": 0},
        }
      }
      ] 
  }
  return update

@bp.route("/create_form", methods=["POST", "GET"])
def create_form():
  if request.method == "POST":
      form = request.form

      week_data = form.get("week")

      parsed_date = parse_date(week_data)
      form_service = build_form_service()
      title ="Online Reservation for {date_range}".format(date_range=parsed_date)
      NEW_FORM = {
          "info": {
              "title": title,
              "documentTitle": title,
          }
      }

      print(parse_body(form))
      result = form_service.forms().create(body=NEW_FORM).execute()
      question_setting = (
          form_service.forms()
          .batchUpdate(formId=result["formId"], body=parse_body(form))
          .execute()
      )
      get_result = form_service.forms().get(formId=result["formId"]).execute()
      
      print(get_result)
      add_form = Form(
          responder_uri=get_result["responderUri"],
          form_id=get_result["formId"],
          week=parsed_date,
      )
      db.session.add(add_form)

      for weekday in ["monday","tuesday","wednesday","thursday","friday"]:
        if form.getlist(weekday):
          for item in form.getlist(weekday):
            print(weekday, item)
            add_options = Options(
              form=add_form,
              food_item=FoodItem.query.get(item),
              weekday=weekday
            )
            db.session.add(add_options)

      db.session.commit()
      return redirect(url_for('index',success=True))
  else:
    food_items = FoodItem.query.all()
    print(FOOD_ITEMS)
    return render_template('create_form.html', food_items=food_items)

@bp.route("/test", methods=["POST", "GET"])
def test():
    food_items = FoodItem.query.all()
    print(FOOD_ITEMS)
    return "ahh"
