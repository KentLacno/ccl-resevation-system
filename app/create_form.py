import json

from flask import (
    Blueprint, redirect, render_template, request,  url_for, session
)

from app.db import db

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
from datetime import timedelta
from app.models import Form
from app.models import FoodItem
from app.models import Options

bp = Blueprint('create_form', __name__, )

SCOPES = ["https://www.googleapis.com/auth/forms.body"]

def build_form_service():
  token = json.loads(session.get("token"))
  creds = Credentials(
    token=token["token"],
    refresh_token=token["refresh_token"],
    token_uri=token["token_uri"],
    client_id=token["client_id"],
    client_secret=token["client_secret"],
    scopes=token["scopes"],
  )
  
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
            "location": {"index": weekday_data["index"]},
          }
        }
    else:
      item = {
          "createItem": {
            "item": {
              "title": (weekday.capitalize()),
              "textItem": {},
            },
            "location": {"index": weekday_data["index"]},
          }
        }
    
    return item
    
  update = {
  "requests": [
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
    },{
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
          "location": {"index": 1}
        }
      },
      ] + list(map(convert_item, weekdays))  
    
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
    return render_template('create_form.html', food_items=food_items)
