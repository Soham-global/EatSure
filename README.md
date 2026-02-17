# 🌍 EatSure (AllergyGuard)

A smart web application that helps people with food allergies safely navigate restaurant menus in any language. Upload a menu photo, and get instant analysis of safe and unsafe dishes based on your allergy profile.

## ✨ Features

- 📸 **Menu Scanning** - Upload or capture menu photos directly from your phone
- 🌐 **Multi-Language Support** - Works with English, Hindi, Arabic, Chinese, and Japanese menus
- 🛡️ **Allergy Detection** - Automatically identifies safe and unsafe dishes based on your allergies
- 💬 **Waiter Communication** - Generates polite messages in the waiter's language to explain your allergies
- 👤 **User Profiles** - Save your allergies and dietary preferences once, use everywhere
- 🎨 **Modern UI** - Clean, responsive design that works on desktop and mobile
- 🔒 **Secure** - User authentication with password hashing

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy
- **OCR**: Tesseract OCR (multi-language text extraction)
- **AI**: Groq API (LLaMA 3.3 70B for menu analysis)
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login

## 📋 Prerequisites

- Python 3.8+
- Tesseract OCR 5.0+
- Groq API Key (free at https://console.groq.com)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd eatSure
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to: `C:\Program Files\Tesseract-OCR`
- Language packs included: English, Hindi, Arabic, Chinese (Simplified), Japanese

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-hin tesseract-ocr-ara tesseract-ocr-jpn tesseract-ocr-chi-sim
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_here
```

**Get your Groq API Key:**
1. Visit https://console.groq.com
2. Sign up for a free account
3. Generate an API key
4. Copy it to your `.env` file

### 5. Run the Application
```bash
python app.py
```

The app will be available at:
- **Local**: http://localhost:8080
- **Network**: http://YOUR_IP:8080 (accessible from phone on same WiFi)

## 📱 Usage

### First Time Setup
1. **Register** - Create an account with username and password
2. **Set Allergies** - Go to Profile and add your allergies (e.g., "peanuts, dairy, gluten")
3. **Add Dietary Notes** - Optional notes like "vegetarian" or "avoid spicy food"

### Scanning a Menu
1. Click **Scan Menu**
2. Take a photo or upload an image of the restaurant menu
3. Select the waiter's language
4. Click **Analyse Menu**
5. View results:
   - ✅ **Safe Dishes** - What you can eat
   - ⚠️ **Unsafe Dishes** - What to avoid
   - 💬 **Waiter Message** - Copy and show to the waiter

## 🌍 Supported Languages

### Menu OCR (Text Extraction)
- 🇬🇧 English
- 🇮🇳 Hindi
- 🇸🇦 Arabic
- 🇨🇳 Chinese (Simplified)
- 🇯🇵 Japanese

### Waiter Communication
The AI can generate messages in any of the above languages to help you communicate your allergies to restaurant staff.

## 📁 Project Structure

```
eatSure/
├── app.py                 # Main Flask application
├── database.py            # Database models
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── instance/
│   └── allergyguard.db   # SQLite database (auto-created)
├── static/
│   └── styles.css        # CSS styling
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── profile.html      # User profile
│   ├── analyse.html      # Menu upload page
│   └── result.html       # Analysis results
└── uploads/              # Uploaded menu images (auto-created)
```

## 🔧 Configuration

### Tesseract Path (Windows)
If Tesseract is installed in a different location, update `app.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Your\Path\To\tesseract.exe'
```

### Port Configuration
To change the port, edit the last line in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change 8080 to your port
```

## 🐛 Troubleshooting

### "Could not extract text from image"
- Ensure the image is clear and well-lit
- Check that Tesseract is properly installed
- Verify language packs are installed

### "Error: Groq API"
- Verify your `GROQ_API_KEY` in `.env` is correct
- Check your internet connection
- Ensure you haven't exceeded API rate limits

### Can't access from phone
- Ensure phone and computer are on the same WiFi network
- Check Windows Firewall allows port 8080
- Try accessing with `http://` (not `https://`)

## 🔒 Security Notes

- Passwords are hashed using Werkzeug's security functions
- Never commit your `.env` file to version control
- Use strong, unique values for `SECRET_KEY`
- For production, use a proper database (PostgreSQL, MySQL)
- Enable HTTPS in production environments

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Groq** - For providing fast LLM inference
- **Tesseract OCR** - For multi-language text recognition
- **Flask** - For the web framework

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

**Made with ❤️ to help people with food allergies eat safely**