from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the model for Client
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone

# Define a simple form
class ClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Route for displaying the form and processing the submission
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ClientForm()

    if form.validate_on_submit():
        # Capture form data
        name = form.name.data
        email = form.email.data
        phone = form.phone.data

        # Create a new client instance and add to the database
        new_client = Client(name=name, email=email, phone=phone)
        db.session.add(new_client)
        db.session.commit()

        # Flash success message
        flash('Client details submitted successfully!', 'success')

        return redirect(url_for('index'))

    return render_template('index.html', form=form)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
