import os.path
import ast
from flask import (
    Blueprint, redirect, render_template, request,  url_for
)
from app.models import Form
from app.models import Options
from app.models import Reservation
from app.db import db

bp = Blueprint('form', __name__, )

@bp.route("/form/<int:FormID>")
def show(FormID):
  form = Form.query.get(FormID)
  reservations = Reservation.query.all()
  
  return render_template('form.html', form=form, loads=ast.literal_eval, reservations=reservations)

@bp.route("/form/<int:FormID>/delete")
def delete(FormID):
  form = Form.query.get(FormID)
  db.session.delete(form)
  db.session.commit()
  
  return redirect(url_for("index"))