from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_wtf import FlaskForm
from forms import ContactForm, RegistrationForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_pymongo import PyMongo
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/institutions_db'
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/about')
def about():
    return render_template('about.html') 

@app.route('/register', methods=['GET', 'POST'] )
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Process form data and store in MongoDB
        user_data = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'password': form.password.data,
            'confirm_password': form.confirm_password.data,
        }
        mongo.db.user_details.insert_one(user_data)

        # Redirect to a thank you page or any other page
        return redirect(url_for('success'))
    return render_template('register.html', form=form)

@app.route('/success')
def success():
    return 'Registration successful!'

@app.route('/login')
def login():
    return render_template('login.html')

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
