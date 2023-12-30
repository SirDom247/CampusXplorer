from flask import Flask, render_template, jsonify, redirect, url_for, request
from flask_security import Security, MongoEngineUserDatastore, UserMixin, RoleMixin, login_required
from flask_pymongo import PyMongo
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/institutions_tert'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'somesalt'

mongo = PyMongo(app)

class Role(mongo.db.Document, RoleMixin):
    name = mongo.db.StringField(max_length=80, unique=True)
    description = mongo.db.StringField(max_length=255)

class User(mongo.db.Document, UserMixin):
    email = mongo.db.StringField(unique=True)
    password = mongo.db.StringField()
    active = mongo.db.BooleanField(default=True)
    roles = mongo.db.ListField(mongo.db.ReferenceField(Role), default=[])

user_datastore = MongoEngineUserDatastore(mongo.db, User, Role)
security = Security(app, user_datastore)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Process the registration logic here (e.g., store user data in a database)
        user_datastore.create_user(email=form.email.data, password=form.password.data)
        return 'Registration successful!'
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Process the login logic here (e.g., validate credentials)
        return 'Login successful!'
    return render_template('login.html', form=form)

@app.route('/search', methods=['POST'])
@login_required
def search():
    data = request.get_json()
    search_term = data.get('search_term', '').lower()

    # Query MongoDB for institutions matching the search term
    results = mongo.db.institutions.find({
        "$or": [
            {"state": {"$regex": f".*{search_term}.*", "$options": "i"}},
            {"institutions.name": {"$regex": f".*{search_term}.*", "$options": "i"}},
        ]
    }, {'_id': 0})

    # Convert MongoDB cursor to a list of dictionaries
    results_list = list(results)

    return jsonify({'results': results_list})

if __name__ == '__main__':
    app.run(debug=True)
