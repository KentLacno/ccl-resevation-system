import os.path

from flask import Flask, render_template, request, redirect, url_for

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
from datetime import timedelta
from food_items import *

SCOPES = ["https://www.googleapis.com/auth/forms.body"]

def build_form_service():
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
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
  def convert_item(weekday):
    if form.getlist(weekday):
      item = {
          "createItem": {
            "item": {
              "title": (weekday.capitalize()),
              "questionItem": {
                "question": {
                  "choiceQuestion": {
                    "type": "CHECKBOX",
                    "options": list(map(lambda e: {"value": e}, form.getlist(weekday))),
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
  "requests": list(map(convert_item, weekdays))
  }
  return update

app = Flask(__name__)

@app.route("/")
def index():
  return render_template('index.html',)

@app.route("/create_form", methods=["POST", "GET"])
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

      return redirect(url_for('index',success=True))
  else:
    print(FOOD_ITEMS)
    return render_template('create_form.html', food_items=FOOD_ITEMS)

if __name__ == "__main__":
  app.run(debug=True)