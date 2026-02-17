import os
import base64
from openai import OpenAI
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image
import pytesseract
from database import db, User

load_dotenv()

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
app.config['SECRET_KEY']              = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///allergyguard.db'
app.config['UPLOAD_FOLDER']           = 'uploads'
app.config['MAX_CONTENT_LENGTH']      = 16 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Groq client (OpenAI-compatible)
client = OpenAI(
    api_key=os.environ.get('GROQ_API_KEY'),
    base_url="https://api.groq.com/openai/v1"
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

UNSAFE_KEYWORDS = [
    'may contain', 'might contain', 'could contain',
    'contains dairy', 'contains peanut', 'contains gluten',
    'contains shellfish', 'contains egg', 'contains soy',
    'not safe', 'not vegetarian', 'not vegan',
    'animal product', 'not suitable', 'cross-contamination'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image(filepath):
    image = Image.open(filepath)
    image = image.convert('L')  # Grayscale
    
    # Use only installed and accurate languages
    attempts = [
        'eng+hin+ara+chi_sim+jpn',  # All installed languages
        'eng+hin',  # Common combination
        'eng',  # Fallback
    ]
    
    best_text = ""
    for lang in attempts:
        try:
            text = pytesseract.image_to_string(image, lang=lang, config='--psm 6')
            if len(text.strip()) > len(best_text.strip()):
                best_text = text
            if len(best_text.strip()) > 50:
                break
        except Exception:
            continue
    
    return best_text.strip()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── PWA Routes ──────────────────────────────────────────────

@app.route('/sw.js')
def service_worker():
    """Serve service worker from root scope (required for PWA)."""
    return send_from_directory('static', 'sw.js',
                               mimetype='application/javascript')

@app.route('/manifest.json')
def manifest():
    """Serve manifest from root (some browsers expect this)."""
    return send_from_directory('static', 'manifest.json',
                               mimetype='application/manifest+json')

@app.route('/offline')
def offline():
    """Offline fallback page shown by service worker."""
    return render_template('offline.html')


# ── App Routes ──────────────────────────────────────────────

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

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
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user     = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


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

        file            = request.files['menu_image']
        waiter_language = request.form.get('waiter_language', 'English')

        if not file or not allowed_file(file.filename):
            flash('Invalid file type. Please upload JPG, PNG or WEBP.', 'error')
            return redirect(url_for('analyse'))

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Enhance image for better OCR
        from PIL import ImageEnhance
        image = Image.open(file)
        image = image.convert('RGB')
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        image.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
        image.save(filepath)

        allergies  = current_user.allergies  or "none"
        diet_notes = current_user.diet_notes or "none"

        try:
            menu_text = extract_text_from_image(filepath)

            if not menu_text.strip():
                flash('Could not extract text from image. Please try a clearer photo.', 'error')
                return redirect(url_for('analyse'))

            prompt = f"""
You are a professional food allergy safety analyzer. Your job is to protect the user from allergens.

User's allergies: {allergies}
User's dietary restrictions: {diet_notes}

Menu text extracted from image:
{menu_text}

INSTRUCTIONS:
1. Identify ALL dishes from the menu
2. For EACH dish, determine if it contains or likely contains ANY of the user's allergens
3. Be CONSERVATIVE - if uncertain, mark as UNSAFE
4. Consider common ingredients (e.g., pasta has gluten, cream has dairy, bread has gluten)
5. Consider cross-contamination risks

RESPONSE FORMAT (follow EXACTLY):

SAFE DISHES:
- [Dish Name]: [Why it's safe - be specific]

UNSAFE DISHES:
- [Dish Name]: [Which allergen(s) it contains]

WAITER MESSAGE ({waiter_language}):
[A polite 2-3 sentence message in {waiter_language} that the user can say to the waiter, explaining their allergies and asking for allergen-free preparation]

IMPORTANT:
- Use bullet points (start with "-") for each dish
- If no safe dishes exist, write "- None found"
- If no unsafe dishes exist, write "- None found"
- Be thorough and check every dish on the menu
"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert food allergy safety analyzer. "
                            "Always prioritize user safety. When in doubt, mark dishes as unsafe. "
                            "Follow the exact output format requested. "
                            "Analyze every dish thoroughly for allergen content."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.2
            )

            result_text = response.choices[0].message.content

            safe_dishes    = []
            unsafe_dishes  = []
            waiter_message = ""
            section        = None

            for line in result_text.split('\n'):
                line = line.strip()

                if 'SAFE DISHES:'   in line: section = 'safe';   continue
                if 'UNSAFE DISHES:' in line: section = 'unsafe'; continue
                if 'WAITER MESSAGE' in line: section = 'waiter'; continue

                if not line: continue
                if line.lower().rstrip(':') == 'none': continue

                if line.startswith('-'):
                    dish       = line[1:].strip()
                    dish_lower = dish.lower()

                    if section == 'unsafe':
                        unsafe_dishes.append(dish)
                    elif section == 'safe':
                        if any(kw in dish_lower for kw in UNSAFE_KEYWORDS):
                            unsafe_dishes.append(dish)
                        else:
                            safe_dishes.append(dish)

                elif section == 'waiter':
                    waiter_message += line + ' '

            return render_template('result.html',
                safe_dishes    = safe_dishes,
                unsafe_dishes  = unsafe_dishes,
                waiter_message = waiter_message.strip(),
                waiter_language= waiter_language
            )

        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for('analyse'))

    return render_template('analyse.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8080)