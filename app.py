# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tip_manager.db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this in production

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    proPic = db.Column(db.String(200))  # Store URL or path to uploaded image
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Tip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    place = db.Column(db.String(200), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    tip_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not all(field in data for field in ['name', 'proPic', 'email', 'password']):
        return jsonify({"message": "invalid field"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(name=data['name'], proPic=data['proPic'], email=data['email'], password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    token = create_access_token(identity={'email': data['email']})
    return jsonify({"name": new_user.name, "token": token}), 201

@app.route('/user/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(identity={'email': user.email})
    return jsonify({"name": user.name, "token": token}), 200

@app.route('/tip/calculate', methods=['POST'])
@jwt_required()
def calculate_tip():
    data = request.get_json()
    if 'place' not in data or 'totalAmount' not in data or 'tipPercentage' not in data:
        return jsonify({"message": "invalid field"}), 400

    total_amount = data['totalAmount']
    tip_percentage = data['tipPercentage']
    tip_amount = (tip_percentage / 100) * total_amount

    # Save the tip record
    user_id = get_jwt_identity()['email']  # or use user ID if preferred
    new_tip = Tip(user_id=user_id, place=data['place'], total_amount=total_amount, tip_amount=tip_amount)
    db.session.add(new_tip)
    db.session.commit()

    return jsonify({"tip": tip_amount}), 200

@app.route('/tip', methods=['GET'])
@jwt_required()
def get_tips():
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    if not start_date or not end_date:
        return jsonify({"message": "Invalid date range"}), 400

    start_date = datetime.strptime(start_date, '%d-%m-%Y')
    end_date = datetime.strptime(end_date, '%d-%m-%Y')

    user_id = get_jwt_identity()['email']  # or use user ID if preferred
    tips = Tip.query.filter(Tip.user_id == user_id, Tip.created_at >= start_date, Tip.created_at <= end_date).all()

    response = [{
        "place": tip.place,
        "totalAmount": tip.total_amount,
        "tipAmount": tip.tip_amount
    } for tip in tips]

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)