from flask import Flask, request, redirect, render_template, session, url_for
import csv
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # needed for sessions

# Owner credentials
OWNER_USERNAME = "madeeha"
OWNER_PASSWORD = "velvet123"

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
            filename = f"products/{category}.csv"
            with open(filename, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([image, title, description, link])
            message = f"{title} added to {category}!"
    return render_template("upload.html", categories=categories, message=message)

# Display products dynamically on category pages
def load_products(category):
    products = []
    try:
        with open(f"products/{category}.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 4:
                    products.append({
                        "image": row[0],
                        "title": row[1],
                        "description": row[2],
                        "link": row[3]
                    })
    except FileNotFoundError:
        pass
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

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)

