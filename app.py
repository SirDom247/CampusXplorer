from flask import Flask, flash, render_template, request, jsonify, redirect, url_for, session
from flask_wtf import FlaskForm
from forms import ContactForm, RegistrationForm, LoginForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

import json 
from dotenv import load_dotenv
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['MONGO_URI'] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/about')
def about():
    return render_template('about.html') 


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
        }
        mongo.db.users.insert_one(user_data)

        # Redirect to a thank you page or any other page
        return redirect(url_for('success'))

    return render_template('register.html', form=form)


@app.route('/success')
def success():
    return render_template('success.html')


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
            flash('Login successful', 'success')  # Flash a success message
            return redirect(url_for('index'))

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

