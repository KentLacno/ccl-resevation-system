
from flask import Flask

from app.db import db
from . import form
from . import create_form
from . import add_respondent
from . import index
from . import food_items
from . import print_reservations

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(index.bp)
app.register_blueprint(form.bp)
app.register_blueprint(create_form.bp)
app.register_blueprint(add_respondent.bp)
app.register_blueprint(food_items.bp)
app.register_blueprint(print_reservations.bp)

app.add_url_rule('/', endpoint='index')

if __name__ == "__main__":
  app.run(debug=True)