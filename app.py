from flask import Flask, request, redirect, render_template, session, url_for
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for sessions

# Owner credentials
OWNER_USERNAME = "madeeha"
OWNER_PASSWORD = "velvet123"

# Database setup
DB_PATH = "products.db"

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            image TEXT,
            title TEXT,
            description TEXT,
            link TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

# Serve main pages
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Login page
@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == OWNER_USERNAME and password == OWNER_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("upload_product"))
        else:
            error = "Invalid credentials"
    return render_template("login.html", error=error)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Product upload page (owner only)
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_product():
    categories = ["fashion", "jewellery", "skincare"]
    message = ""
    if request.method == "POST":
        category = request.form.get("category")
        title = request.form.get("title")
        description = request.form.get("description")
        image = request.form.get("image")
        link = request.form.get("link")

        if category in categories:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (category, image, title, description, link) VALUES (?, ?, ?, ?, ?)",
                (category, image, title, description, link)
            )
            conn.commit()
            conn.close()
            message = f"{title} added to {category}!"
    return render_template("upload.html", categories=categories, message=message)

# Display products dynamically on category pages
def load_products(category):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT image, title, description, link FROM products WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    products = []
    for row in rows:
        products.append({
            "image": row[0],
            "title": row[1],
            "description": row[2],
            "link": row[3]
        })
    return products

@app.route("/fashion")
def fashion():
    products = load_products("fashion")
    return render_template("fashion.html", products=products)

@app.route("/jewellery")
def jewellery():
    products = load_products("jewellery")
    return render_template("jewellery.html", products=products)

@app.route("/skincare")
def skincare():
    products = load_products("skincare")
    return render_template("skincare.html", products=products)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
