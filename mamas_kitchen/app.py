from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import Cook, Customer, Meal, Rating
import os
import logging
import sqlite3
from flask import jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import base64
from datetime import datetime




# Initialize Flask app
app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Load config and secret key
app.config.from_pyfile('config.py')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Set the folder to save uploaded files
app.config['UPLOAD_FOLDER'] = 'static/profile_images'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5501"]}}, supports_credentials=True)

# Check if the file has a valid extension

# Enable CORS with credentials


# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()
    app.logger.info("✅ Database tables created")

@app.route('/')
def home():
    return "✅ Mama's Kitchen API is running!"

#-------------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to upload a profile image
@app.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save the file path to the database (e.g., for the user profile)
        # Update the user's profile with the image path, assuming `cook_id` is known
        cook_id = request.form['cook_id']  # Example: getting cook ID from form data
        update_profile_image_in_db(cook_id, filename)

        return redirect(url_for('profile', cook_id=cook_id))  # Redirect to the profile page
    return 'Invalid file type', 400

# Function to update profile image path in the database
def update_profile_image_in_db(cook_id, filename):
    # Update the user's profile in the database (example function)
    # This assumes you have a database set up and a table to store user data
    pass

# Route to display the cook's profile page
@app.route('/profile/<int:cook_id>')
def profile(cook_id):
    # Get cook profile from the database
    user = Cook.query.get(cook_id)
    profile_image = user.profile_image if user.profile_image else 'default_profile_image.jpg'

    # Rating logic
    customer_id = session.get('user_id') if session.get('user_type') == 'customer' else None
    user_rating = None
    if customer_id:
        rating_entry = Rating.query.filter_by(cook_id=cook_id, customer_id=customer_id).first()
        if rating_entry:
            user_rating = rating_entry.rating_value

    # Get average rating for cook
    avg_rating = db.session.query(db.func.avg(Rating.rating_value)).filter_by(cook_id=cook_id).scalar()
    avg_rating = round(avg_rating, 1) if avg_rating else None

    return render_template('profile.html',
                           cook=user,
                           profile_image=profile_image,
                           user_rating=user_rating,
                           average_rating=avg_rating)




# -------------------------- LOGIN --------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    cook = Cook.query.filter_by(cook_email=email).first()
    customer = Customer.query.filter_by(customer_email=email).first()

    if cook and check_password_hash(cook.cook_pass, password):
        session['cook_id'] = cook.cook_id
        session['user_type'] = 'cook'
        session['name'] = cook.cook_name

        return jsonify({
            'message': 'Login successful',
            'user_type': 'cook',
            'user_id': cook.cook_id,
            'name': cook.cook_name,
            'email': cook.cook_email
        }), 200

    if customer and check_password_hash(customer.customer_pass, password):
        session['customer_id'] = customer.customer_id
        session['user_type'] = 'customer'
        session['name'] = customer.customer_name

        return jsonify({
            'message': 'Login successful',
            'user_type': 'customer',
            'user_id': customer.customer_id,
            'name': customer.customer_name,
            'email': customer.customer_email
        }), 200

    return jsonify({'message': 'Invalid email or password'}), 401

# ---------------------- SESSION CHECK -----------------------
@app.route('/check_session')
def check_session():
    if 'customer_id' in session:
        return jsonify({
            'logged_in': True,
            'user_type': 'customer',
            'user_id': session['customer_id'],
            'customer_id': session['customer_id']  # ✅ ensure this exists
        })
    elif 'cook_id' in session:
        return jsonify({
            'logged_in': True,
            'user_type': 'cook',
            'user_id': session['cook_id'],
            'cook_id': session['cook_id']  # ✅ ensure this exists
        })
    return jsonify({'logged_in': False})




# ------------------ CUSTOMER REGISTRATION -------------------
@app.route('/customer/register', methods=['POST'])
def register_customer():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not all([name, email, password]):
            return jsonify({'error': 'All fields are required'}), 400

        if Customer.query.filter_by(customer_email=email).first() or Cook.query.filter_by(cook_email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        new_customer = Customer(
            customer_name=name,
            customer_email=email,
            customer_pass=generate_password_hash(password)
        )

        db.session.add(new_customer)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'customer_id': new_customer.customer_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

# ------------------- COOK REGISTRATION ----------------------
@app.route('/cook/register', methods=['POST'])
def register_cook():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['name', 'email', 'password', 'gender', 'location', 'phone']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'All fields are required'}), 400

        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password'].strip()
        gender = data['gender'].strip()
        location = data['location'].strip()
        phone = data['phone'].strip()

        if Customer.query.filter_by(customer_email=email).first() or Cook.query.filter_by(cook_email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        new_cook = Cook(
            cook_name=name,
            cook_email=email,
            cook_pass=generate_password_hash(password),
            cook_gender=gender,
            cook_location=location,
            cook_phone=phone
        )

        db.session.add(new_cook)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'cook_id': new_cook.cook_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

# ---------------------- GET ALL COOKS -----------------------
@app.route('/cooks', methods=['GET'])
def get_all_cooks():
    try:
        cooks = Cook.query.all()
        cook_list = [{
            'id': cooks.cook_id,
            'name': cooks.cook_name,
            'email': cooks.cook_email,
            'gender': cooks.cook_gender,
            'location': cooks.cook_location,
            'phone': cooks.cook_phone
        } for cooks in cooks]
        return jsonify({'cooks': cook_list})
    except Exception as e:
        return jsonify({'message': 'Server error fetching cooks'}), 500

# ---------------------- GET COOK PROFILE --------------------
@app.route('/cooks/<int:cook_id>', methods=['GET'])
def get_cook_profile(cook_id):
    cook = Cook.query.filter_by(cook_id=cook_id).first()
    if cook:
        # Calculate the average rating
        ratings = Rating.query.filter_by(cook_id=cook_id).all()
        average_rating = sum(rating.rating_value for rating in ratings) / len(ratings) if ratings else None

    return jsonify({
        'cook': {
            'id': cook.cook_id,
            'name': cook.cook_name,
            'email': cook.cook_email,
            'gender': cook.cook_gender,
            'location': cook.cook_location,
            'phone': cook.cook_phone,
            "average_rating": average_rating   # ✅ added here
        }
    })
    

# ---------------------- GET MEALS BY COOK -------------------
@app.route('/meals/<int:cook_id>', methods=['GET'])
def get_meals_by_cook(cook_id):
    meals = db.session.query(Meal).filter(Meal.cook_id == cook_id).all()

    meal_list = [{
        'name': meal.meal_name,
        'price': float(meal.meal_price),
        'description': meal.meal_recipe,
        'image': base64.b64encode(meal.image.tobytes()).decode('utf-8') if isinstance(meal.image, memoryview) else meal.image
    } for meal in meals]

    return jsonify({"meals": meal_list})



# ---------------------- UPLOAD MEAL -------------------------
@app.route('/add_meal', methods=['POST'])
def add_meal():
    # Get the cook ID from session only
    cook_id = request.form.get("cook_id")

    app.logger.debug(f"Session cook_id: {cook_id}")
    
    meal_name = request.form.get('meal_name')
    meal_price = request.form.get('meal_price')
    meal_recipe = request.form.get('recipe')
    image_file = request.files.get('image')

    if not all([meal_name, meal_price, meal_recipe, image_file]):
        return jsonify({"success": False, "error": "Missing fields"}), 400

    image_bytes = image_file.read()

    new_meal = Meal(
        meal_name=meal_name,
        meal_price=meal_price,
        meal_recipe=meal_recipe,
        image=image_bytes,
        cook_id=cook_id  # Securely assign cook_id from session
    )

    db.session.add(new_meal)
    db.session.commit()
    app.logger.debug(f"Adding meal for cook_id from session: {cook_id}")


    return jsonify({"success": True})
#--------------------------------------
@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    try:
        # 1. Get and validate request data
        data = request.get_json()
        if not data:
            app.logger.error("No JSON data received")
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        app.logger.debug(f"Received rating data: {data}")

        # 2. Validate required fields
        required_fields = ['customer_id', 'cook_id', 'rating_value']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            app.logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # 3. Validate data types and values
        try:
            customer_id = int(data['customer_id'])
            cook_id = int(data['cook_id'])
            rating_value = int(data['rating_value'])
            
            if not (1 <= rating_value <= 5):
                raise ValueError("Rating must be between 1-5")
                
        except (ValueError, TypeError) as e:
            app.logger.error(f"Invalid data format: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Invalid data format: ' + str(e)
            }), 400

        # 4. Check if customer and cook exist
        customer = Customer.query.get(customer_id)
        cook = Cook.query.get(cook_id)
        
        if not customer:
            app.logger.error(f"Customer not found: {customer_id}")
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
            
        if not cook:
            app.logger.error(f"Cook not found: {cook_id}")
            return jsonify({
                'success': False,
                'message': 'Cook not found'
            }), 404

        # 5. Create or update rating
        rating = Rating.query.filter_by(
            customer_id=customer_id,
            cook_id=cook_id
        ).first()

        if rating:
            app.logger.debug(f"Updating existing rating (ID: {rating.rating_id}) from {rating.rating_value} to {rating_value}")
            rating.rating_value = rating_value
            action = 'updated'
        else:
            app.logger.debug(f"Creating new rating for customer {customer_id} and cook {cook_id}")
            rating = Rating(
                customer_id=customer_id,
                cook_id=cook_id,
                rating_value=rating_value,
                rating_date=datetime.utcnow()
            )
            db.session.add(rating)
            action = 'created'

        # 6. Commit changes
        db.session.commit()
        app.logger.info(f"New rating saved with ID: {rating.rating_id}")


        # 7. Calculate new average rating
        avg_rating = db.session.query(
            db.func.avg(Rating.rating_value)
        ).filter_by(cook_id=cook_id).scalar()
        avg_rating = round(float(avg_rating), 1) if avg_rating else None

        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully',
            'rating_id': rating.rating_id,
            'rating_value': rating_value,
            'average_rating': avg_rating,
            'action': action
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error'
        }), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred'
        }), 500

    
#----------------------------------------------






# ---------------------- DEBUG USER --------------------------
@app.route('/debug/user', methods=['POST'])
def debug_user():
    data = request.get_json(silent=True)
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

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
            'match': check_password_hash(cook.cook_pass, password)
        }
    if customer:
        result['customer_data'] = {
            'stored_password': customer.customer_pass,
            'match': check_password_hash(customer.customer_pass, password)
        }

    return jsonify(result)

# ---------------- LOGGING REQUESTS --------------------------
@app.before_request
def log_request_info():
    app.logger.debug(f"\n{'='*50}\nRequest: {request.method} {request.path}")
    if request.is_json:
        app.logger.debug(f"JSON Body: {request.get_json(silent=True)}")
    else:
        app.logger.debug(f"Raw Body: {request.get_data()}")
    app.logger.debug(f"{'='*50}\n")

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5501'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# ---------------------- MAIN ENTRY --------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5000)
