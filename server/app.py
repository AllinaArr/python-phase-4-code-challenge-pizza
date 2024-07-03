#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=['GET'])
def get_restaurants():
    data = Restaurant.query.all()
    if request.method == 'GET':
        return [d.to_dict(rules = ['-restaurant_pizzas']) for d in data], 200

@app.route("/restaurants/<int:id>", methods=['GET', 'DELETE'])
def get_rest_by_id(id):
    restourant = Restaurant.query.filter(Restaurant.id == id).first()

    if not restourant:
            return {"error": "Restaurant not found"}, 404
        
    if request.method == 'GET':
        return restourant.to_dict(), 200
    elif request.method == 'DELETE':
        db.session.delete(restourant)
        db.session.commit()
        return make_response(restourant.to_dict(), 204)
    
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return [p.to_dict(rules = ['-restaurant_pizzas']) for p in pizzas], 200
    
@app.route('/restaurant_pizzas', methods=['POST'])
def post_pizzas():
    if request.method=='POST':
        data = request.get_json()
    
        try:
            new_rest_pizza = RestaurantPizza(
                price = data['price'],
                pizza_id = data['pizza_id'],
                restaurant_id = data['restaurant_id']
            )
        except ValueError:
                return {'errors':["validation errors"]}, 400
        
        db.session.add(new_rest_pizza)
        db.session.commit()
    
        return make_response((new_rest_pizza.to_dict()), 201)
    
    
if __name__ == "__main__":
    app.run(port=5555, debug=True)
