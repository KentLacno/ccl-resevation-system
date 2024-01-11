import json
from flask import (
    Blueprint, redirect, render_template, session
)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

bp = Blueprint('login', __name__, )

SCOPES = ["https://www.googleapis.com/auth/script.scriptapp", "https://www.googleapis.com/auth/script.external_request", "https://www.googleapis.com/auth/forms","https://www.googleapis.com/auth/forms.body"]

@bp.route("/login")
def login():

  creds = None
  try:
    token = json.loads(session.get("token"))
    creds = Credentials(
      token=token["token"],
      refresh_token=token["refresh_token"],
      token_uri=token["token_uri"],
      client_id=token["client_id"],
      client_secret=token["client_secret"],
      scopes=token["scopes"],
      )
  except:
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
        else:
          flow = InstalledAppFlow.from_client_secrets_file(
              "credentials.json", SCOPES
          )
          creds = flow.run_local_server(port=0)
          session["token"] = creds.to_json()
          return redirect("/")
  return redirect("/")