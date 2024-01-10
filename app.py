from flask import Flask, flash, render_template, request, jsonify, redirect, url_for, session
from flask_wtf import FlaskForm
from forms import ContactForm, RegistrationForm, LoginForm
from wtforms import StringField, TextAreaField, SubmitField
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from wtforms.validators import DataRequired, Email, Length
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

import json 
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['MONGO_URI'] = os.getenv("MONGO_URI")

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
mongo = PyMongo(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# User model 
class User(UserMixin):
    def __init__(self, username, first_name, last_name, email, password, is_admin=False):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_admin = is_admin
        
@login_manager.user_loader
def load_user(username):
    user_data = mongo.db.users.find_one({'username': username})
    if user_data:
        return User(username=user_data['username'], first_name=user_data['first_name'], last_name=user_data['last_name'], password=user_data['password'], email=user_data['email'], is_admin=user_data['is_admin'])
    return None

@app.route('/')
def index():
    return render_template('base.html')


@app.route('/about')
def about():
    return render_template('about.html') 


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()

    if form.validate_on_submit():
        admin = mongo.db.admins.find_one({'username': form.username.data})

        if admin and bcrypt.check_password_hash(admin['password'], form.password.data):
            # Log the admin in
            session['admin_logged_in'] = True
            flash('Admin login successful', 'success')
            return redirect(url_for('admin_dashboard'))
        
        admin_data = {
            'username': 'admin',
            'password': bcrypt.generate_password_hash('admin_password').decode('utf-8'),
                # Add other fields as needed
            }
        mongo.db.admins.insert_one(admin_data)
        flash('Admin account created successfully', 'success')
    
    flash('Invalid admin credentials', 'error')

    return render_template('admin_login.html', form=form)

@app.route('/admin/dashboard')
def admin_dashboard():
    # Add authentication check for admin
    if not session.get('admin_logged_in'):
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))

    return render_template('base.html')

@app.route('/admin/logout')
def admin_logout():
    # Clear the session data for the admin
    session.pop('admin_logged_in', None)
    flash('Admin logout successful', 'success')
    return redirect(url_for('index'))


# admin-only route
@app.route('/admin/manage_users')
def manage_users():
    # authentication check for admin
    if not session.get('admin_logged_in'):
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))

    # logic for managing users
    return render_template('manage_users.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Compare the entered password with the confirm password before hashing
        if form.password.data != form.confirm_password.data:
            flash('Password and Confirm Password do not match', 'error')
            return redirect(url_for('register'))

        # Hash the password using Flask-Bcrypt
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Process form data and store in MongoDB
        user_data = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'username': form.username.data,       
            'email': form.email.data,
            'password': hashed_password,
            'is_admin': form.username.data == 'admin',  # Assign admin role based on username
        }
        mongo.db.users.insert_one(user_data)

        flash('Account created successfully.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/user_dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Retrieve the user from the database based on the provided email
        user = mongo.db.users.find_one({'email': form.email.data})

        # Check if the user exists and the password is valid
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            # Log the user in by storing data in the session
            session['logged_in'] = True
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']

            is_admin = user.get('is_admin', False)
            return redirect(url_for('admin_dashboard') if is_admin else 'user_dashboard')
        
        flash('Login successful', 'success')  # Flash a success message
        return redirect(url_for('admin_dashboard' if user.get('is_admin', False) else ''))
        # Invalid login, show an error message or redirect as needed
    flash('Invalid email or password', 'error')  # Flash an error message

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    # Clear the session data for the user
    session.clear()
    flash('Logout successful', 'success')  # Flash a success message
    return redirect(url_for('index'))


@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    form = ContactForm()

    if form.validate_on_submit():
            # Process form data and store in MongoDB
            user_data = {
            'username': form.username.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'message': form.message.data
        }
            mongo.db.user_details.insert_one(user_data)

            # Redirect to a thank you page or any other page
            return redirect(url_for('thank_you'))

    return render_template('contact_us.html', form=form)


@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/insert_data', methods=['GET'])
def insert_data_into_mongo():
    try:
        # Read data from package.json file
        with open('package.json', 'r') as file:
            data = json.load(file)

        # Insert data into MongoDB
        mongo.db.institutions.insert_many(data['institutions'])
        return 'Data inserted into MongoDB successfully.'
    except Exception as e:
        return f'Error inserting data: {str(e)}'

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    search_term = data.get('search_term', '').lower()
    
    # Query MongoDB for institutions matching the search term
    results = mongo.db.institutions.find({
        "state": {"$regex": f".*{search_term}.*", "$options": "i"}
    }, {'_id': 0})
        
    # Convert MongoDB cursor to a list of dictionaries
    results_list = list(results)
    return jsonify({'results': results_list})


# Insert data into MongoDB on startup
insert_data_into_mongo()

if __name__ == '__main__':
    app.run(debug=True)

