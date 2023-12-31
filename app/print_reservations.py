import os.path
import ast
from flask import (
    Blueprint, redirect, render_template, request,  url_for
)
from app.models import Form
from app.models import Respondent
from app.models import Reservation

bp = Blueprint('print_reservations', __name__, )

@bp.route("/print_reservations/<int:FormID>")
def print(FormID):
  form = Form.query.get(FormID)
  respondents = Respondent.query.filter_by(form=form, paid=True)
    
  return render_template('print_reservations.html', respondents=respondents, Reservation=Reservation, form_id=form.id)