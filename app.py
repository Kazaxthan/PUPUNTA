from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    student_id = db.Column(db.String(20), nullable=True, unique=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)

class CarFareCalculator:
    def __init__(self, base_fare, fare_per_km, fare_per_minute):
        self.base_fare = base_fare
        self.fare_per_km = fare_per_km
        self.fare_per_minute = fare_per_minute

    def calculate_fare(self, trip_distance, trip_duration):
        fare = self.base_fare + (trip_distance * self.fare_per_km) + (trip_duration * self.fare_per_minute)
        return fare

class MotorcycleFareCalculator:
    def __init__(self):
        pass

    def calculate_fare(self, trip_distance, trip_duration):
        if trip_distance <= 1:
            fare = 50
        elif 1 < trip_distance <= 2:
            fare = 50
        elif 2 < trip_distance <= 7:
            fare = 50 + (trip_distance - 2) * 10
        else:
            fare = 50 + 5 * 10 + (trip_distance - 7) * 15
        return fare

motor_fare = {
    'base_fare': 50,  # PHP
    'fare_per_km': 10,  # PHP per km
    'fare_per_minute': 2  # PHP per minute
}

four_seater_fare = {
    'base_fare': 50,  # PHP
    'fare_per_km': 10,  # PHP per km
    'fare_per_minute': 2  # PHP per minute
}

six_seater_fare = {
    'base_fare': 70,  # PHP
    'fare_per_km': 15,  # PHP per km
    'fare_per_minute': 3  # PHP per minute
}

four_seater_calculator = CarFareCalculator(**four_seater_fare)
six_seater_calculator = CarFareCalculator(**six_seater_fare)
motorcycle_calculator = MotorcycleFareCalculator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('book_ride'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        student_id = request.form['student_id']
        full_name = request.form['full_name']
        email = request.form['email']

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(username=username, password=hashed_password, student_id=student_id, full_name=full_name, email=email)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/book_ride', methods=['GET', 'POST'])
def book_ride():
    if 'user_id' in session:
        if request.method == 'POST':
            vehicle_type = request.form.get('vehicle')
            pickup_location = request.form.get('pickup')
            destination = request.form.get('destination')

            if not vehicle_type or not pickup_location or not destination:
                flash('Please fill out all fields and select locations on the map.')
                return redirect(url_for('book_ride'))

            pickup_coords = pickup_location.split(',')
            destination_coords = destination.split(',')

            api_key = 'your_api_key'
            url = f'https://graphhopper.com/api/1/route?point={pickup_coords[0]},{pickup_coords[1]}&point={destination_coords[0]},{destination_coords[1]}&vehicle=car&key={api_key}&points_encoded=false&type=json'

            try:
                response = requests.get(url)
                route_data = response.json()
                if 'paths' in route_data:
                    route_geometry = route_data['paths'][0]['points']['coordinates']
                    trip_distance = route_data['paths'][0]['distance'] / 1000  # convert to km
                    trip_duration = route_data['paths'][0]['time'] / 60000  # convert to minutes

                    if vehicle_type == 'car':
                        fare = four_seater_calculator.calculate_fare(trip_distance, trip_duration)
                    elif vehicle_type == 'bike':
                        fare = motorcycle_calculator.calculate_fare(trip_distance, trip_duration)

                    flash(f'Ride booked successfully! Estimated fare: {fare:.2f} PHP')
                    return render_template('book_ride.html', route=json.dumps(route_geometry))
                else:
                    flash('Route not found. Please try again.')
                    return redirect(url_for('book_ride'))
            except Exception as e:
                flash(f'Error fetching route: {e}')
                return redirect(url_for('book_ride'))

        return render_template('book_ride.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
