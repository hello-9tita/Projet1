from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pyodbc

# Initialize Flask app
app = Flask(__name__)

# Configure Azure SQL Database (environment variable for security)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://wissal:DocHelp_server@dochelp-server.database.windows.net/DBdoc?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Doctor model
class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

# User model for appointments
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

# Appointment model
class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date_time = db.Column(db.String(50), nullable=False)

    # Relationships
    user = db.relationship('User', backref='appointments', lazy=True)
    doctor = db.relationship('Doctor', backref='appointments', lazy=True)

# Route to render the main page
@app.route('/')
def index():
    return render_template('frontend.html')

# Route to handle the form submission
@app.route('/map', methods=['POST'])
def search_doctor():
    specialty = request.form['specialty']
    location = request.form['location']

    # Query doctors based on specialty and location
    doctors = Doctor.query.filter_by(specialty=specialty, location=location).all()
    return render_template('map.html', doctors=doctors)

# Route to create an appointment
@app.route('/appointment', methods=['POST'])
def make_appointment():
    user_name = request.form['name']
    user_email = request.form['email']
    user_phone = request.form['phone']
    doctor_id = request.form['doctor_id']
    appointment_date_time = request.form['date_time']

    # Create or retrieve user
    user = User.query.filter_by(email=user_email).first()
    if not user:
        user = User(name=user_name, email=user_email, phone=user_phone)
        db.session.add(user)
        db.session.commit()

    # Create appointment
    appointment = Appointment(user_id=user.id, doctor_id=doctor_id, date_time=appointment_date_time)
    db.session.add(appointment)
    db.session.commit()

    return "Appointment booked successfully!"

if __name__ == '__main__':
    app.run(debug=True)
