import os
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image
from database import db, User

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY']           = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///allergyguard.db'
app.config['UPLOAD_FOLDER']        = 'uploads'
app.config['MAX_CONTENT_LENGTH']   = 16 * 1024 * 1024  # 16MB max
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel("gemini-2.5-flash")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Routes ──────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user     = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        allergies  = request.form.get('allergies', '')
        diet_notes = request.form.get('diet_notes', '')
        current_user.allergies  = allergies
        current_user.diet_notes = diet_notes
        db.session.commit()
        flash('Profile updated successfully!', 'success')

    return render_template('profile.html', user=current_user)

@app.route('/analyse', methods=['GET', 'POST'])
@login_required
def analyse():
    if request.method == 'POST':
        if 'menu_image' not in request.files:
            flash('No file uploaded.', 'error')
            return redirect(url_for('analyse'))

        file = request.files['menu_image']
        waiter_language = request.form.get('waiter_language', 'English')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # --- RESIZING LOGIC ---
            # Open the image file
            image = Image.open(file)
            # Resize to max 1024px to save tokens and stay in the Free Tier
            image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            # Save the resized image to the server
            image.save(filepath)

            # Build info from user profile
            allergies = current_user.allergies or "none"
            diet_notes = current_user.diet_notes or "none"

            prompt = f"User Allergies: {allergies}. Notes: {diet_notes}. Format: SAFE DISHES, UNSAFE DISHES, WAITER MESSAGE ({waiter_language})."

            try:
                # --- CORRECT MODEL NAME FOR 2026 ---
                # Ensure you are using the specific string "gemini-2.5-flash-image"
                current_model = genai.GenerativeModel("gemini-2.5-flash-image")
                
                # Pass the resized image object directly
                response = current_model.generate_content([prompt, image])
                result_text = response.text

                # --- Your existing parsing logic below ---
                safe_dishes, unsafe_dishes, waiter_message = [], [], ""
                lines = result_text.split('\n')
                section = None
                for line in lines:
                    line = line.strip()
                    if 'SAFE DISHES:' in line: section = 'safe'
                    elif 'UNSAFE DISHES:' in line: section = 'unsafe'
                    elif 'WAITER MESSAGE' in line: section = 'waiter'
                    elif line.startswith('-') and section == 'safe': safe_dishes.append(line[1:].strip())
                    elif line.startswith('-') and section == 'unsafe': unsafe_dishes.append(line[1:].strip())
                    elif section == 'waiter' and line: waiter_message += line + ' '

                return render_template('result.html', safe_dishes=safe_dishes, unsafe_dishes=unsafe_dishes, waiter_message=waiter_message.strip(), waiter_language=waiter_language)

            except Exception as e:
                flash(f"Model Error: {str(e)}. The model version may have updated. Check ai.google.dev.", "error")
                return redirect(url_for('analyse'))

    return render_template('analyse.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)