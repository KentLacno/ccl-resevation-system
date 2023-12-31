import os.path
import ast
from flask import (
    Blueprint, redirect, render_template, request,  url_for
)
from app.models import Form
from app.models import Options
from app.models import Reservation

bp = Blueprint('form', __name__, )

@bp.route("/form/<int:FormID>")
def show(FormID):
  form = Form.query.get(FormID)
  reservations = Reservation.query.all()
  
  return render_template('form.html', form=form, loads=ast.literal_eval, reservations=reservations)

