import json

from flask import (
    Blueprint, redirect, render_template, request,  url_for, session
)

from app.db import db

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.models import Form

bp = Blueprint('index', __name__, )

SCOPES = ["https://www.googleapis.com/auth/script.scriptapp", "https://www.googleapis.com/auth/script.external_request", "https://www.googleapis.com/auth/forms"]

def build_script_service():
  token = json.loads(session.get("token"))
  creds = Credentials(
    token=token["token"],
    refresh_token=token["refresh_token"],
    token_uri=token["token_uri"],
    client_id=token["client_id"],
    client_secret=token["client_secret"],
    scopes=token["scopes"],
  )
  
  script_service = build("script", "v1", credentials=creds)
  return script_service

@bp.route("/")
def index():
  if not session.get("token"):
    return redirect("/login")
  print(session.get("token"))
  alert = request.args.get('alert')
  primary_form = Form.query.filter_by(primary=True).first()
  forms = Form.query.filter_by(primary=False)

  return render_template('index.html', primary_form=primary_form, forms=forms, alert=alert)

@bp.route("/set_active_property/<int:FormID>/<string:redirect_to>", methods=['POST'])
def set_active_property(FormID, redirect_to):
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

  if redirect_to == "form":
    return redirect(url_for('form.show', FormID=FormID))
  elif redirect_to == "index":
    return redirect(url_for('index'))
  
@bp.route("/set_primary_property/<int:FormID>/<string:redirect_to>", methods=['POST'])
def set_primary_property(FormID, redirect_to):
  form = Form.query.get(FormID)

  if not form.primary and Form.query.filter_by(primary=True).first():
      return redirect(url_for('index', alert="primary_error"))
  
  form.primary = not form.primary
  db.session.commit()

  if redirect_to == "form":
    return redirect(url_for('form.show', FormID=FormID))
  elif redirect_to == "index":
    return redirect(url_for('index'))