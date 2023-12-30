import os.path
import ast
import json
import requests

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
from food_items import *

bp = Blueprint('index', __name__, )

SCOPES = ["https://www.googleapis.com/auth/script.scriptapp", "https://www.googleapis.com/auth/script.external_request", "https://www.googleapis.com/auth/forms"]

def build_script_service():
  creds = None
  if os.path.exists("script_token.json"):
    try:
      creds = Credentials.from_authorized_user_file("script_token.json", SCOPES)
    except:
      if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
        else:
          flow = InstalledAppFlow.from_client_secrets_file(
              "credentials.json", SCOPES
          )
          creds = flow.run_local_server(port=0)
        with open("script_token.json", "w") as token:
          token.write(creds.to_json())

  script_service = build("script", "v1", credentials=creds)
  return script_service

@bp.route("/")
def index():
  alert = request.args.get('alert')
  primary_form = Form.query.filter_by(primary=True).first()
  forms = Form.query.filter_by(primary=False)

  return render_template('index.html', primary_form=primary_form, forms=forms, alert=alert)

@bp.route("/set_active_property/<int:FormID>", methods=['POST'])
def set_active_property(FormID):
  form = Form.query.get(FormID)
  script_service = build_script_service()
  script_id = "1-p9s-qcaqMkoVZnn84OJj5XOsrgvcfrFCXBaXN4QwTqzo_6x-jTkJ6qc"

  if not form.active:
    request = {
      "function": "setUpTrigger",
      "parameters": [
        form.form_id
      ],
      "devMode": True
    }

  elif form.active:
    request = {
      "function": "deleteTrigger",
      "parameters": [
        form.trigger_id
      ],
      "devMode": True
    }

  response = script_service.scripts().run(scriptId=script_id, body=request).execute()
  form.trigger_id = response["response"].get("result", {}) if not form.active else None
 
  form.active = not form.active 
  db.session.commit()

  return redirect(url_for('index'))

@bp.route("/set_primary_property/<int:FormID>", methods=['POST'])
def set_primary_property(FormID):
  form = Form.query.get(FormID)

  if not form.primary and Form.query.filter_by(primary=True).first():
      return redirect(url_for('index', alert="primary_error"))
  
  form.primary = not form.primary
  db.session.commit()

  return redirect(url_for('index'))