from flask import Flask, render_template, request, redirect, session, url_for, send_file
import os
import PyPDF2

app = Flask(__name__)
app.secret_key = "nexahire_pro_99_key"
app.config['UPLOAD_FOLDER'] = "/tmp"

# Upload folder check
# --- ATS LOGIC (Pro Analysis) ---
def analyze_resume(text):
    categories = {
        "Technical Skills": ["python", "sql", "html", "css", "java", "javascript", "react", "flask", "aws", "git"],
        "Soft Skills": ["leadership", "communication", "teamwork", "management", "problem solving"],
        "Education": ["degree", "bachelor", "master", "university", "college", "graduate"],
        "Contact Details": ["phone", "email", "@", "linkedin", "github"]
    }
    
    strengths = []
    weaknesses = []
    points = 0
    
    for category, keywords in categories.items():
        found = [word for word in keywords if word in text]
        if found:
            strengths.append(category)
            points += 1
        else:
            weaknesses.append(category)

    score = int((points / len(categories)) * 100)
    
    if score < 50:
        msg = "Low score? Build a high-scoring resume instantly."
    elif score < 80:
        msg = "Almost there! Perfect your resume with our AI tools."
    else:
        msg = "Great score! Your resume is recruiter-ready."
        
    return score, strengths, weaknesses, msg

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        # Login successful - setting session
        session['user'] = username
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('resume')
    if file and file.filename.endswith('.pdf'):
        filename = file.filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        
        # Save path for download functionality
        session['last_file'] = path 
        
        text = ""
        try:
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content = page.extract_text()
                    if content: text += content.lower()
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

        # AI Analysis
        score, strengths, weaknesses, msg = analyze_resume(text)
        
        return render_template('result.html', 
                               score=score, 
                               strengths=strengths, 
                               weaknesses=weaknesses, 
                               message=msg)
    
    return redirect(url_for('home'))
# --- SIGNUP ROUTE (Correct Logic) ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        # Session-la data-ah save panrom
        session['user'] = username
        session['fullname'] = fullname
        
        # Login successful aanathukku aprom home-ku redirect panrom
        return redirect(url_for('home'))
        
    return render_template('signup.html')

@app.route('/download')
def download():
    path = session.get('last_file')
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True, download_name="NexaHire_Analysis_Report.pdf")
    return "Error: File not found!", 404
