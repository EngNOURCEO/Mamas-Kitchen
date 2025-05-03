# models.py

from database import db
from datetime import datetime


class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255))
    customer_email = db.Column(db.String(255), unique=True)
    customer_pass = db.Column(db.String(255))

class Cook(db.Model):
    __tablename__ = 'cook'
    cook_id = db.Column(db.Integer, primary_key=True)
    cook_name = db.Column(db.String(255))
    cook_email = db.Column(db.String(255), unique=True)
    cook_pass = db.Column(db.String(255))
    cook_gender = db.Column(db.String(50))
    cook_location = db.Column(db.String(255))
    cook_phone = db.Column(db.String(20))

class Meal(db.Model):
    __tablename__ = 'meal'
    meal_id = db.Column(db.Integer, primary_key=True)
    cook_id = db.Column(db.Integer, db.ForeignKey('cook.cook_id', ondelete='CASCADE'))
    meal_recipe = db.Column(db.Text)
    image = db.Column(db.Text)
    meal_price = db.Column(db.Numeric(10,2))
    meal_name = db.Column(db.String(255))


class Rating(db.Model):
    __tablename__ = 'rating'

    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id', ondelete='CASCADE'), nullable=False)
    cook_id = db.Column(db.Integer, db.ForeignKey('cook.cook_id', ondelete='CASCADE'), nullable=False)

    rating_date = db.Column(db.Date, default=datetime.utcnow)
    rating_value = db.Column(db.Integer, nullable=False)

    customer = db.relationship('Customer', backref=db.backref('ratings_given', lazy=True))
    cook = db.relationship('Cook', backref=db.backref('ratings_received', lazy=True))



class CookMeal(db.Model):
    __tablename__ = 'cook_meal'
    cook_id = db.Column(db.Integer, db.ForeignKey('cook.cook_id', ondelete='CASCADE'), primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.meal_id', ondelete='CASCADE'), primary_key=True)

class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_email = db.Column(db.String(255), unique=True)
    admin_pass = db.Column(db.String(255))
