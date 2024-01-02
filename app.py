# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Function to connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('zoo.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create the database tables
def init_db():
    with app.app_context():
        conn = get_db_connection()
        with app.open_resource('schema.sql', mode='r') as f:
            conn.cursor().executescript(f.read())
        conn.commit()
        conn.close()

# Check if the database file exists, otherwise initialize the database
if not os.path.exists('zoo.db'):
    init_db()

# Define the routes

# Home page
@app.route('/')
def index():
    conn = get_db_connection()
    animals = conn.execute('SELECT * FROM animals').fetchall()
    conn.close()
    return render_template('index.html', animals=animals)

# Add animal page
@app.route('/add', methods=['GET', 'POST'])
def add_animal():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        species = request.form['species']
        photo = request.files['photo']

        if not name or not age or not species or not photo:
            flash('All fields are required.')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO animals (name, age, species, photo) VALUES (?, ?, ?, ?)',
                         (name, age, species, photo.filename))
            conn.commit()
            conn.close()

            photo.save(os.path.join('static/uploads', photo.filename))
            flash('Animal added successfully.')

    return render_template('add.html')

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('All fields are required.')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, generate_password_hash(password)))
            conn.commit()
            conn.close()
            flash('Registration successful. Please log in.')

    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

# ... (previous code)

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# ... (rest of your routes)

# ... (previous code)

# Update animal page
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_animal(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    animal = conn.execute('SELECT * FROM animals WHERE id = ?', (id,)).fetchone()
    conn.close()

    if animal is None:
        flash('Animal not found.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        species = request.form['species']
        photo_url = request.form['photo_url']

        if not name or not age or not species or not photo_url:
            flash('All fields are required.')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE animals SET name = ?, age = ?, species = ?, photo_url = ? WHERE id = ?',
                         (name, age, species, photo_url, id))
            conn.commit()
            conn.close()

            flash('Animal updated successfully.')
            return redirect(url_for('index'))

    return render_template('update.html', animal=animal)

# Delete animal page
@app.route('/delete/<int:id>')
def delete_animal(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM animals WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Animal deleted successfully.')
    return redirect(url_for('index'))

# ... (rest of your routes)



# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

# Run the application
if __name__ == '__main__':
    app.run(debug=True)