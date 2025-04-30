from flask import Flask, jsonify, request
from flask_cors import CORS
from database import db
from models import Cook, Customer
import os
import logging

# Initialize Flask app
app = Flask(_name_)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5000", 
            "http://127.0.0.1:5000", 
            "http://127.0.0.1:5501"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Load configuration
app.config.from_pyfile('config.py')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    app.logger.info("Database tables created")

@app.route('/')
def home():
    return "✅ Mama's Kitchen API is running!"

#-----------------------------------------------------------

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Check both tables
        cook = Cook.query.filter_by(cook_email=email).first()
        customer = Customer.query.filter_by(customer_email=email).first()
        
        if cook and cook.cook_pass == password:
            app.logger.debug(f"Cook login successful: {email}")
            return jsonify({
                'message': 'Login successful',
                'user_type': 'cook',
                'user_id': cook.cook_id,
                'name': cook.cook_name,
                'email': cook.cook_email
            }), 200
            
        if customer and customer.customer_pass == password:
            app.logger.debug(f"Customer login successful: {email}")
            return jsonify({
                'message': 'Login successful',
                'user_type': 'customer',
                'user_id': customer.customer_id,
                'name': customer.customer_name,
                'email': customer.customer_email
            }), 200
        
        # If we get here, login failed
        app.logger.debug(f"Login failed for email: {email}")
        return jsonify({'message': 'Invalid email or password'}), 401
        
    except Exception as e:
        app.logger.error(f'Login error: {str(e)}', exc_info=True)
        return jsonify({'message': 'Server error during authentication'}), 500

#---------------------------------------------------------------

@app.route('/customer/register', methods=['POST'])
def register_customer():
    try:
        data = request.get_json()
        app.logger.debug(f"Registration attempt with data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not all([name, email, password]):
            return jsonify({'error': 'All fields are required'}), 400

        # Check if email exists in either table
        if (Customer.query.filter_by(customer_email=email).first() or 
            Cook.query.filter_by(cook_email=email).first()):
            return jsonify({'error': 'Email already registered'}), 400

        new_customer = Customer(
            customer_name=name,
            customer_email=email,
            customer_pass=password
        )

        db.session.add(new_customer)
        db.session.commit()
        app.logger.info(f"New customer registered: {email}")

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'customer_id': new_customer.customer_id
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Registration failed: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'Registration failed',
            'details': str(e)
        }), 500

###---------------------------------------------------------

@app.route('/debug/user', methods=['POST'])
def debug_user():
    """Check if email exists in either table"""
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    
    cook = Cook.query.filter_by(cook_email=email).first()
    customer = Customer.query.filter_by(customer_email=email).first()
    
    result = {
        'email': email,
        'exists_in_cook': bool(cook),
        'exists_in_customer': bool(customer),
        'exists': bool(cook or customer)
    }
    
    if cook:
        result['cook_data'] = {
            'stored_password': cook.cook_pass,
            'match': cook.cook_pass == data.get('password', '')
        }
    if customer:
        result['customer_data'] = {
            'stored_password': customer.customer_pass,
            'match': customer.customer_pass == data.get('password', '')
        }
    
    return jsonify(result)

#######---------------------------------

@app.route('/cook/register', methods=['POST'])
def register_cook():
    try:
        data = request.get_json()
        app.logger.debug(f"Cook registration attempt with data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['name', 'email', 'password', 'gender', 'location', 'phone']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'All fields are required'}), 400

        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        gender = data.get('gender', '').strip()
        location = data.get('location', '').strip()
        phone = data.get('phone', '').strip()

        # Check if email exists in either table
        if (Customer.query.filter_by(customer_email=email).first() or 
            Cook.query.filter_by(cook_email=email).first()):
            return jsonify({'error': 'Email already registered'}), 400

        new_cook = Cook(
            cook_name=name,
            cook_email=email,
            cook_pass=password,
            cook_gender=gender,
            cook_location=location,
            cook_phone=phone
        )

        db.session.add(new_cook)
        db.session.commit()
        app.logger.info(f"New cook registered: {email}")

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'cook_id': new_cook.cook_id
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Cook registration failed: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'Registration failed',
            'details': str(e)
        }), 500

###3-----------------------------------------

@app.route('/cooks', methods=['GET'])
def get_all_cooks():
    try:
        cooks = Cook.query.all()
        cook_list = []
        for cook in cooks:
            cook_list.append({
                'id': cook.cook_id,
                'name': cook.cook_name,
                'email': cook.cook_email,
                'gender': cook.cook_gender,
                'location': cook.cook_location,
                'phone': cook.cook_phone
            })
        
        app.logger.debug(f"Cook data: {cook_list}")  # سجل البيانات في الخادم
        return jsonify({'cooks': cook_list})
    
    except Exception as e:
        app.logger.error(f"Error fetching cooks: {str(e)}", exc_info=True)
        return jsonify({'message': 'Server error fetching cooks'}), 500

# Main entry point
@app.before_request
def log_request_info():
    app.logger.debug(f"\n{'='*50}\nRequest: {request.method} {request.path}")
    app.logger.debug(f"Headers: {dict(request.headers)}")
    if request.is_json:
        app.logger.debug(f"JSON Body: {request.get_json()}")
    else:
        app.logger.debug(f"Raw Body: {request.get_data()}")
    app.logger.debug(f"{'='*50}\n")

if _name_ == '_main_':
    app.run(debug=True, host='0.0.0.0',port=5000)
