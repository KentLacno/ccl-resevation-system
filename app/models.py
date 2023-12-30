from app.db import db

class Form(db.Model):
    __tablename__ = "form"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    form_id = db.Column(db.Text, unique=True, nullable=False)
    trigger_id = db.Column(db.Text, unique=True)
    primary = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.current_timestamp())
    responder_uri = db.Column(db.Text)
    week = db.Column(db.String(10), nullable=False)
    respondents = db.relationship("Respondent", backref="form")
    options = db.relationship("Options", backref="form")
    

class Respondent(db.Model):
    __tablename__ = "respondent"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    grade_section = db.Column(db.Text)
    form_id = db.Column(db.Integer, db.ForeignKey('form.form_id'))
    reservations = db.relationship("Reservation", backref="respondent")

class Options(db.Model):
    __tablename__ = "options"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'))
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'))
    weekday = db.Column(db.Text)

class Reservation(db.Model):
    __tablename__ = "reservation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    respondent_id = db.Column(db.Integer, db.ForeignKey('respondent.id'))
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'))
    weekday = db.Column(db.Text)

class FoodItem(db.Model):
    __tablename__ = "food_item"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reservations = db.relationship("Reservation", backref="food_item")
    options = db.relationship("Options", backref="food_item")
    name = db.Column(db.Text)
    value = db.Column(db.Text)
    image = db.Column(db.Text)
    price = db.Column(db.Integer)

