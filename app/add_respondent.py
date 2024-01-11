import re
from flask import (
    Blueprint, request,
)

from app.models import Form
from app.models import Respondent
from app.models import FoodItem
from app.models import Reservation
from app.db import db

bp = Blueprint('add_respondent', __name__, )

@bp.route("/add_respondent", methods=["POST"])
def add_respondent():
  if request.method == "POST":
    response = request.json
    print(response)
    form = Form.query.filter_by(form_id=response["form_id"]).first()
    
    add_respondent = Respondent(
          name=response["name"],
          grade_section=response["grade and section"],
          form=form,
      )
    
    for weekday in ["monday","tuesday","wednesday","thursday","friday"]:
      if weekday in response:
        format_ids = list(map(lambda item: int(re.findall(r"(?<=\()\d(?=\))",item)[0]), response[weekday]))
        queries = list(map(lambda id: FoodItem.query.get(id), format_ids))
        for query in queries:
          add_reservation = Reservation(
            respondent=add_respondent,
            food_item=query,
            weekday=weekday
          )
          db.session.add(add_reservation)

    db.session.add(add_respondent)
    db.session.commit()
    return "ahh"
    